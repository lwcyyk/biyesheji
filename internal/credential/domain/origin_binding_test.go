package domain

import (
	"testing"

	"vdns.local/vdns/internal/cryptokit"
	"vdns.local/vdns/internal/protocol"
)

func TestOriginBindingUsesCanonicalOriginAndAccount(t *testing.T) {
	nameKey := testOriginNameKey(t)
	originA, err := NormalizeOrigin("HTTPS://Example.COM:443/")
	if err != nil {
		t.Fatal(err)
	}
	defer originA.Destroy()
	originB, err := NormalizeOrigin("https://example.com")
	if err != nil {
		t.Fatal(err)
	}
	defer originB.Destroy()
	originOther, err := NormalizeOrigin("https://other.example")
	if err != nil {
		t.Fatal(err)
	}
	defer originOther.Destroy()

	bindingA, err := ComputeOriginBinding(nameKey, originA, []byte("alice@example.test"))
	if err != nil {
		t.Fatal(err)
	}
	bindingB, err := ComputeOriginBinding(nameKey, originB, []byte("alice@example.test"))
	if err != nil {
		t.Fatal(err)
	}
	if bindingA != bindingB {
		t.Fatal("equivalent canonical origins produced different bindings")
	}
	otherAccount, _ := ComputeOriginBinding(nameKey, originB, []byte("bob@example.test"))
	if bindingA == otherAccount {
		t.Fatal("different accounts produced the same binding")
	}
	otherOrigin, _ := ComputeOriginBinding(nameKey, originOther, []byte("alice@example.test"))
	if bindingA == otherOrigin {
		t.Fatal("different origins produced the same binding")
	}
}

func TestOriginBindingFailsClosedAfterOriginOrKeyDestruction(t *testing.T) {
	nameKey := testOriginNameKey(t)
	origin, err := NormalizeOrigin("https://secret.example")
	if err != nil {
		t.Fatal(err)
	}
	origin.Destroy()
	if binding, bindErr := ComputeOriginBinding(nameKey, origin, []byte("alice")); bindErr != ErrOriginBinding || binding != [cryptokit.OriginBindingSize]byte{} {
		t.Fatalf("destroyed origin binding = %x, %v", binding, bindErr)
	}

	liveOrigin, _ := NormalizeOrigin("https://secret.example")
	defer liveOrigin.Destroy()
	nameKey.Destroy()
	if binding, bindErr := ComputeOriginBinding(nameKey, liveOrigin, []byte("alice")); bindErr != ErrOriginBinding || binding != [cryptokit.OriginBindingSize]byte{} {
		t.Fatalf("destroyed name key binding = %x, %v", binding, bindErr)
	}
}

func testOriginNameKey(t *testing.T) *cryptokit.Key {
	t.Helper()
	root, err := cryptokit.NewSecret(bytesForOriginBinding(cryptokit.KeySize, 1))
	if err != nil {
		t.Fatal(err)
	}
	defer root.Destroy()
	var namespaceID protocol.NamespaceID
	copy(namespaceID[:], bytesForOriginBinding(len(namespaceID), 41))
	prk, err := cryptokit.ExtractNamespacePRK(root, namespaceID, 1)
	if err != nil {
		t.Fatal(err)
	}
	defer prk.Destroy()
	keys, err := cryptokit.DeriveNamespaceKeys(prk)
	if err != nil {
		t.Fatal(err)
	}
	keys.Wrap.Destroy()
	keys.Audit.Destroy()
	keys.Relation.Destroy()
	keys.Rotation.Destroy()
	t.Cleanup(keys.Name.Destroy)
	return keys.Name
}

func bytesForOriginBinding(size int, start byte) []byte {
	result := make([]byte, size)
	for index := range result {
		result[index] = start + byte(index)
	}
	return result
}
