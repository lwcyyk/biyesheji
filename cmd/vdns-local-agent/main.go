// Command vdns-local-agent starts the authenticated loopback API and serves a
// persistent Native Messaging connection on stdin/stdout. It expects an
// already initialized CP-2 vault profile; initialization is intentionally a
// separate ceremony.
package main

import (
	"bytes"
	"context"
	"encoding/base64"
	"errors"
	"flag"
	"fmt"
	"net"
	"net/http"
	"os"
	"strings"
	"time"

	"vdns.local/vdns/internal/adapters/inbound/httpapi"
	"vdns.local/vdns/internal/adapters/inbound/nativemessaging"
	sqliteadapter "vdns.local/vdns/internal/adapters/outbound/sqlite"
	"vdns.local/vdns/internal/cryptokit"
	localapp "vdns.local/vdns/internal/localapi/application"
	"vdns.local/vdns/internal/protocol"
)

type options struct {
	databasePath     string
	namespaceText    string
	deviceText       string
	deviceSecretPath string
	installTokenPath string
	extensionID      string
}

func main() {
	var options options
	flag.StringVar(&options.databasePath, "db", "", "initialized VDNS-PM SQLite database")
	flag.StringVar(&options.namespaceText, "namespace", "", "base64url NamespaceID")
	flag.StringVar(&options.deviceText, "device", "", "base64url DeviceID")
	flag.StringVar(&options.deviceSecretPath, "device-secret-file", "", "0600 file containing a 32-byte base64url device secret")
	flag.StringVar(&options.installTokenPath, "install-token-file", "", "0600 file containing the loopback installation token")
	flag.StringVar(&options.extensionID, "extension-id", "", "32-character Chrome extension ID")
	flag.Parse()
	if err := run(options); err != nil {
		_, _ = fmt.Fprintln(os.Stderr, "vdns-local-agent:", stableStartupError(err))
		os.Exit(1)
	}
}

func run(options options) error {
	namespaceID, err := protocol.ParseNamespaceID(options.namespaceText)
	if err != nil {
		return errors.New("invalid namespace configuration")
	}
	deviceID, err := protocol.ParseDeviceID(options.deviceText)
	if err != nil || !validExtensionID(options.extensionID) {
		return errors.New("invalid device or extension configuration")
	}
	deviceSecretBytes, err := readRestrictedBase64Secret(options.deviceSecretPath, cryptokit.KeySize)
	if err != nil {
		return errors.New("device secret file rejected")
	}
	defer clear(deviceSecretBytes)
	deviceSecret, err := cryptokit.NewSecret(deviceSecretBytes)
	if err != nil {
		return errors.New("device secret file rejected")
	}
	defer deviceSecret.Destroy()
	tokenBytes, err := readRestrictedBase64Secret(options.installTokenPath, 32)
	if err != nil {
		return errors.New("installation token file rejected")
	}
	installToken := base64.RawURLEncoding.EncodeToString(tokenBytes)
	clear(tokenBytes)
	defer func() { installToken = "" }()

	ctx := context.Background()
	database, err := sqliteadapter.Open(ctx, options.databasePath)
	if err != nil {
		return errors.New("database initialization failed")
	}
	defer database.Close()
	profiles, err := sqliteadapter.NewVaultProfileRepository(database)
	if err != nil {
		return errors.New("vault profile repository unavailable")
	}
	localStore, err := sqliteadapter.NewLocalAPIRepository(database)
	if err != nil {
		return errors.New("local API repository unavailable")
	}
	unlock := func(deviceText string, master *cryptokit.Secret) error {
		requested, parseErr := protocol.ParseDeviceID(deviceText)
		if parseErr != nil || requested != deviceID {
			return cryptokit.ErrRejectCapsule
		}
		record, loadErr := profiles.Load(context.Background(), namespaceID, deviceID)
		if loadErr != nil {
			return cryptokit.ErrRejectCapsule
		}
		bundle, openErr := cryptokit.OpenRootCapsule(
			master, deviceSecret, namespaceID, deviceID, record.RootCapsule,
		)
		if openErr != nil {
			return cryptokit.ErrRejectCapsule
		}
		bundle.Destroy()
		return nil
	}
	recoverVault := func(namespaceText, _ string, recovery *cryptokit.Secret) error {
		requested, parseErr := protocol.ParseNamespaceID(namespaceText)
		if parseErr != nil || requested != namespaceID {
			return cryptokit.ErrRejectCapsule
		}
		record, loadErr := profiles.Load(context.Background(), namespaceID, deviceID)
		if loadErr != nil {
			return cryptokit.ErrRejectCapsule
		}
		bundle, openErr := cryptokit.OpenRecoveryCapsule(
			recovery, namespaceID, record.RecoveryCapsule,
		)
		if openErr != nil {
			return cryptokit.ErrRejectCapsule
		}
		bundle.Destroy()
		return nil
	}
	agent, err := localapp.NewAgent(localapp.Config{
		UnlockVerifier: unlock, RecoveryVerifier: recoverVault,
	})
	if err != nil {
		return errors.New("local application initialization failed")
	}
	api, err := httpapi.New(agent, httpapi.Config{
		InstallToken: installToken,
		AllowedExtensionOrigins: []string{
			"chrome-extension://" + options.extensionID,
		},
		IdempotencyStore: localStore,
		OperationStore:   localStore,
	})
	if err != nil {
		return errors.New("local HTTP adapter initialization failed")
	}
	listener, err := net.Listen("tcp4", "127.0.0.1:0")
	if err != nil {
		return errors.New("loopback listener unavailable")
	}
	defer listener.Close()
	server := &http.Server{
		Handler: api, ReadHeaderTimeout: 3 * time.Second,
		ReadTimeout: 10 * time.Second, WriteTimeout: 10 * time.Second,
		IdleTimeout: 30 * time.Second, MaxHeaderBytes: 16 * 1024,
	}
	serverErrors := make(chan error, 1)
	go func() {
		err := server.Serve(listener)
		if !errors.Is(err, http.ErrServerClosed) {
			serverErrors <- err
		}
		close(serverErrors)
	}()
	host, err := nativemessaging.New(agent, nativemessaging.Config{
		BaseURL: "http://" + listener.Addr().String(), InstallToken: installToken,
	})
	if err != nil {
		_ = server.Close()
		return errors.New("Native Messaging initialization failed")
	}
	runErr := host.Run(os.Stdin, os.Stdout)
	shutdownContext, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()
	_ = server.Shutdown(shutdownContext)
	select {
	case serveErr := <-serverErrors:
		if serveErr != nil {
			return errors.New("loopback server failed")
		}
	default:
	}
	return runErr
}

func readRestrictedBase64Secret(path string, expectedBytes int) ([]byte, error) {
	if strings.TrimSpace(path) == "" || expectedBytes < 1 {
		return nil, errors.New("invalid secret file")
	}
	info, err := os.Lstat(path)
	if err != nil || !info.Mode().IsRegular() || info.Mode().Perm()&0o077 != 0 {
		return nil, errors.New("invalid secret file permissions")
	}
	encoded, err := os.ReadFile(path)
	if err != nil || len(encoded) > 4096 {
		clear(encoded)
		return nil, errors.New("invalid secret file")
	}
	trimmed := bytes.TrimSpace(encoded)
	decoded := make([]byte, base64.RawURLEncoding.DecodedLen(len(trimmed)))
	written, err := base64.RawURLEncoding.Decode(decoded, trimmed)
	clear(encoded)
	if err != nil || written != expectedBytes {
		clear(decoded)
		return nil, errors.New("invalid secret file encoding")
	}
	return decoded[:written], nil
}

func validExtensionID(value string) bool {
	if len(value) != 32 {
		return false
	}
	for _, current := range value {
		if current < 'a' || current > 'p' {
			return false
		}
	}
	return true
}

func stableStartupError(err error) string {
	if err == nil {
		return "unknown startup failure"
	}
	allowed := err.Error()
	if len(allowed) > 160 || strings.ContainsAny(allowed, "\r\n/\\") {
		return "startup rejected"
	}
	return allowed
}
