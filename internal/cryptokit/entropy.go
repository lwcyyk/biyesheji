package cryptokit

import (
	"crypto/rand"
	"io"
)

// EntropySource carries both a reader and an explicit production-safety bit.
// Only SystemEntropySource is production-safe. Test readers are deliberately
// tainted and rejected by exported encryption entry points.
type EntropySource struct {
	reader   io.Reader
	testOnly bool
}

// SystemEntropySource returns the operating system CSPRNG.
func SystemEntropySource() EntropySource {
	return EntropySource{reader: rand.Reader}
}

// NewTestOnlyEntropySource labels an injected reader as test-only. Passing it
// to SealEventWithEntropy or EncryptFieldWithEntropy fails closed; package
// tests use unexported helpers to exercise deterministic vectors.
func NewTestOnlyEntropySource(reader io.Reader) EntropySource {
	return EntropySource{reader: reader, testOnly: true}
}

func (source EntropySource) productionReader() (io.Reader, error) {
	if source.reader == nil || source.testOnly {
		return nil, ErrRandomSource
	}
	return source.reader, nil
}

func fillRandom(reader io.Reader, destination []byte) error {
	if reader == nil || len(destination) == 0 {
		return ErrRandomSource
	}
	if _, err := io.ReadFull(reader, destination); err != nil {
		wipe(destination)
		return ErrRandomSource
	}
	return nil
}
