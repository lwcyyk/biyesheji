package platform

import "time"

// SystemClock is the production UTC display/retrieval clock.
type SystemClock struct{}

func (SystemClock) Now() time.Time { return time.Now().UTC() }
