package platform

import "testing"

func TestSystemClockReturnsUTC(t *testing.T) {
	if got := (SystemClock{}).Now(); got.Location().String() != "UTC" {
		t.Fatalf("clock location = %q, want UTC", got.Location())
	}
}
