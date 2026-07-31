package cryptokit

import (
	"crypto/rand"
	"errors"
	"io"
	"sort"
	"time"

	"golang.org/x/crypto/argon2"
)

const (
	MinArgon2CalibrationTarget  = 500 * time.Millisecond
	MaxArgon2CalibrationTarget  = 1500 * time.Millisecond
	MinArgon2CalibrationSamples = 3
	MaxArgon2CalibrationSamples = 9
)

var ErrArgon2Calibration = errors.New("ARGON2_CALIBRATION_FAILED")

// Argon2CalibrationPolicy defines one bounded first-run benchmark. Memory and
// lanes remain fixed while the calibrator chooses the highest iteration count
// whose measured P95 does not exceed TargetP95.
type Argon2CalibrationPolicy struct {
	TargetP95 time.Duration
	MemoryKiB uint32
	Lanes     uint8
	Samples   int
}

// Argon2CalibrationResult is safe to persist alongside public profile data.
type Argon2CalibrationResult struct {
	Params          Argon2Params
	MeasuredP95     time.Duration
	TargetP95       time.Duration
	WithinTarget    bool
	SamplesPerRound int
}

// DefaultArgon2CalibrationPolicy targets the middle of the normative
// 0.5–1.5-second range while retaining the desktop memory baseline.
func DefaultArgon2CalibrationPolicy() Argon2CalibrationPolicy {
	return Argon2CalibrationPolicy{
		TargetP95: time.Second,
		MemoryKiB: DefaultArgon2Params.MemoryKiB,
		Lanes:     DefaultArgon2Params.Lanes,
		Samples:   3,
	}
}

// CalibrateArgon2id performs the bounded first-run benchmark using independent
// random calibration material. It never benchmarks the user's real password.
func CalibrateArgon2id(policy Argon2CalibrationPolicy) (Argon2CalibrationResult, error) {
	password := make([]byte, KeySize)
	var salt [Argon2SaltSize]byte
	if _, err := io.ReadFull(rand.Reader, password); err != nil {
		wipe(password)
		return Argon2CalibrationResult{}, ErrArgon2Calibration
	}
	defer wipe(password)
	if _, err := io.ReadFull(rand.Reader, salt[:]); err != nil {
		wipe(salt[:])
		return Argon2CalibrationResult{}, ErrArgon2Calibration
	}
	defer wipe(salt[:])

	return calibrateArgon2id(policy, func(params Argon2Params) (time.Duration, error) {
		started := time.Now()
		output := argon2.IDKey(
			password,
			salt[:],
			params.Iterations,
			params.MemoryKiB,
			params.Lanes,
			KeySize,
		)
		elapsed := time.Since(started)
		wipe(output)
		return elapsed, nil
	})
}

type argon2MeasureFunc func(Argon2Params) (time.Duration, error)

func calibrateArgon2id(
	policy Argon2CalibrationPolicy,
	measure argon2MeasureFunc,
) (Argon2CalibrationResult, error) {
	if policy.TargetP95 < MinArgon2CalibrationTarget ||
		policy.TargetP95 > MaxArgon2CalibrationTarget ||
		policy.Samples < MinArgon2CalibrationSamples ||
		policy.Samples > MaxArgon2CalibrationSamples ||
		measure == nil {
		return Argon2CalibrationResult{}, ErrArgon2Calibration
	}
	base := Argon2Params{
		Version: Argon2Version, MemoryKiB: policy.MemoryKiB,
		Iterations: MinArgon2Iterations, Lanes: policy.Lanes,
	}
	if err := base.Validate(); err != nil {
		return Argon2CalibrationResult{}, ErrArgon2Calibration
	}

	var selected Argon2CalibrationResult
	for iterations := MinArgon2Iterations; iterations <= MaxArgon2Iterations; iterations++ {
		candidate := base
		candidate.Iterations = iterations
		durations := make([]time.Duration, policy.Samples)
		for sample := range durations {
			duration, err := measure(candidate)
			if err != nil || duration <= 0 || duration > MaxArgon2CalibrationTarget*4 {
				return Argon2CalibrationResult{}, ErrArgon2Calibration
			}
			durations[sample] = duration
		}
		p95 := durationPercentile(durations, 95)
		result := Argon2CalibrationResult{
			Params: candidate, MeasuredP95: p95, TargetP95: policy.TargetP95,
			WithinTarget: p95 <= policy.TargetP95, SamplesPerRound: policy.Samples,
		}
		if iterations == MinArgon2Iterations {
			selected = result
		}
		if p95 > policy.TargetP95 {
			break
		}
		selected = result
	}
	return selected, nil
}

func durationPercentile(values []time.Duration, percentile int) time.Duration {
	ordered := append([]time.Duration(nil), values...)
	sort.Slice(ordered, func(left, right int) bool { return ordered[left] < ordered[right] })
	index := (percentile*len(ordered) + 99) / 100
	if index < 1 {
		index = 1
	}
	return ordered[index-1]
}
