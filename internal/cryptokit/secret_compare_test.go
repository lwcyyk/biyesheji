package cryptokit

import (
	"errors"
	"testing"
)

func TestSecretsEqualWithoutExposingMaterial(t *testing.T) {
	t.Parallel()
	left, _ := NewSecret([]byte("same-secret"))
	same, _ := NewSecret([]byte("same-secret"))
	different, _ := NewSecret([]byte("different-secret"))
	shorter, _ := NewSecret([]byte("same"))
	defer left.Destroy()
	defer same.Destroy()
	defer different.Destroy()
	defer shorter.Destroy()
	if equal, err := SecretsEqual(left, same); err != nil || !equal {
		t.Fatalf("equal secrets = %v, %v", equal, err)
	}
	for _, candidate := range []*Secret{different, shorter} {
		if equal, err := SecretsEqual(left, candidate); err != nil || equal {
			t.Fatalf("different secrets = %v, %v", equal, err)
		}
	}
	left.Destroy()
	if _, err := SecretsEqual(left, same); !errors.Is(err, ErrSecretDestroyed) {
		t.Fatalf("destroyed secret error = %v", err)
	}
}
