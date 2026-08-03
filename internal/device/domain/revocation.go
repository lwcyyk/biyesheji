package domain

import (
	"errors"
	"sort"

	"vpass.local/vpass/internal/protocol"
)

var (
	ErrInvalidRevocationPlan = errors.New("invalid device revocation plan")
	ErrRevocationOrder       = errors.New("device revocation step is out of order")
)

type RemediationStatus string

const (
	RemediationCompleted RemediationStatus = "COMPLETED"
	RemediationPending   RemediationStatus = "PENDING"
	RemediationFailed    RemediationStatus = "FAILED"
	RemediationUnknown   RemediationStatus = "UNKNOWN"
)

func (status RemediationStatus) Valid() bool {
	switch status {
	case RemediationCompleted, RemediationPending, RemediationFailed, RemediationUnknown:
		return true
	default:
		return false
	}
}

type CredentialSet struct {
	values map[protocol.CredentialID]struct{}
}

type KnownCredentialSet = CredentialSet
type FutureAccessBlockedSet = CredentialSet
type RemediationRequiredSet = CredentialSet

func NewCredentialSet(values []protocol.CredentialID) (CredentialSet, error) {
	set := CredentialSet{values: make(map[protocol.CredentialID]struct{}, len(values))}
	for _, value := range values {
		if deviceBytesZero(value[:]) {
			return CredentialSet{}, ErrInvalidRevocationPlan
		}
		set.values[value] = struct{}{}
	}
	return set, nil
}

func (set CredentialSet) Contains(value protocol.CredentialID) bool {
	_, ok := set.values[value]
	return ok
}

func (set CredentialSet) Len() int { return len(set.values) }

func (set CredentialSet) IDs() []protocol.CredentialID {
	result := make([]protocol.CredentialID, 0, len(set.values))
	for value := range set.values {
		result = append(result, value)
	}
	sort.Slice(result, func(i, j int) bool {
		return string(result[i][:]) < string(result[j][:])
	})
	return result
}

func (set *CredentialSet) add(value protocol.CredentialID) {
	if set.values == nil {
		set.values = make(map[protocol.CredentialID]struct{})
	}
	set.values[value] = struct{}{}
}

func (set *CredentialSet) remove(value protocol.CredentialID) {
	delete(set.values, value)
}

type RevocationLayerStatus string

const (
	LayerPending   RevocationLayerStatus = "PENDING"
	LayerCompleted RevocationLayerStatus = "COMPLETED"
	LayerFailed    RevocationLayerStatus = "FAILED"
	LayerUnknown   RevocationLayerStatus = "UNKNOWN"
)

type RevocationSnapshot struct {
	RevokedDeviceID           protocol.DeviceID
	OldSecretGeneration       uint64
	NewSecretGeneration       uint64
	ControlPlaneStatus        RevocationLayerStatus
	ControlFinalSequence      uint64
	SecretIsolationStatus     RevocationLayerStatus
	ExternalRemediationStatus RemediationStatus
	KnownCredentialSet        []protocol.CredentialID
	FutureAccessBlockedSet    []protocol.CredentialID
	RemediationRequiredSet    []protocol.CredentialID
	RemediationByCredential   map[protocol.CredentialID]RemediationStatus
}

type DeviceRevocationPlan struct {
	snapshot RevocationSnapshot
	known    KnownCredentialSet
	blocked  FutureAccessBlockedSet
	required RemediationRequiredSet
}

func NewDeviceRevocationPlan(
	revokedDeviceID protocol.DeviceID,
	oldGeneration uint64,
	knownCredentials []protocol.CredentialID,
) (*DeviceRevocationPlan, error) {
	if deviceBytesZero(revokedDeviceID[:]) || oldGeneration == 0 {
		return nil, ErrInvalidRevocationPlan
	}
	known, err := NewCredentialSet(knownCredentials)
	if err != nil {
		return nil, err
	}
	required, _ := NewCredentialSet(knownCredentials)
	return &DeviceRevocationPlan{
		snapshot: RevocationSnapshot{
			RevokedDeviceID: revokedDeviceID, OldSecretGeneration: oldGeneration,
			ControlPlaneStatus: LayerPending, SecretIsolationStatus: LayerPending,
			ExternalRemediationStatus: RemediationPending,
			RemediationByCredential:   make(map[protocol.CredentialID]RemediationStatus),
		},
		known:    known,
		blocked:  CredentialSet{values: make(map[protocol.CredentialID]struct{})},
		required: required,
	}, nil
}

// FinalizeControlPlane makes operations at or after the revocation sequence
// invalid. Historical signatures remain verifiable.
func (plan *DeviceRevocationPlan) FinalizeControlPlane(finalSequence uint64) error {
	if plan == nil || plan.snapshot.ControlPlaneStatus != LayerPending ||
		finalSequence == 0 {
		return ErrRevocationOrder
	}
	plan.snapshot.ControlPlaneStatus = LayerCompleted
	plan.snapshot.ControlFinalSequence = finalSequence
	return nil
}

func (plan *DeviceRevocationPlan) OperationAllowed(
	deviceID protocol.DeviceID,
	finalSequence uint64,
) bool {
	if plan == nil || finalSequence == 0 {
		return false
	}
	if deviceID != plan.snapshot.RevokedDeviceID {
		return true
	}
	if plan.snapshot.ControlPlaneStatus != LayerCompleted {
		return false
	}
	return finalSequence < plan.snapshot.ControlFinalSequence
}

// CompleteSecretIsolation records that a independently random new generation
// was issued only to the supplied active recipients.
func (plan *DeviceRevocationPlan) CompleteSecretIsolation(
	newGeneration uint64,
	recipients []protocol.DeviceID,
) error {
	if plan == nil || plan.snapshot.ControlPlaneStatus != LayerCompleted ||
		plan.snapshot.SecretIsolationStatus != LayerPending ||
		newGeneration <= plan.snapshot.OldSecretGeneration || len(recipients) == 0 {
		return ErrRevocationOrder
	}
	seen := make(map[protocol.DeviceID]bool, len(recipients))
	for _, recipient := range recipients {
		if deviceBytesZero(recipient[:]) || recipient == plan.snapshot.RevokedDeviceID ||
			seen[recipient] {
			return ErrInvalidRevocationPlan
		}
		seen[recipient] = true
	}
	plan.snapshot.NewSecretGeneration = newGeneration
	plan.snapshot.SecretIsolationStatus = LayerCompleted
	for _, credentialID := range plan.known.IDs() {
		plan.blocked.add(credentialID)
	}
	return nil
}

func (plan *DeviceRevocationPlan) CanReceiveGeneration(
	deviceID protocol.DeviceID,
	generation uint64,
) bool {
	if plan == nil || deviceID == plan.snapshot.RevokedDeviceID {
		return false
	}
	return plan.snapshot.SecretIsolationStatus == LayerCompleted &&
		generation == plan.snapshot.NewSecretGeneration
}

// HistoricalCredentialMayStillWork is deliberately true for credentials the
// revoked device knew until an external remediation is COMPLETED.
func (plan *DeviceRevocationPlan) HistoricalCredentialMayStillWork(
	credentialID protocol.CredentialID,
) bool {
	return plan != nil && plan.known.Contains(credentialID) &&
		plan.required.Contains(credentialID)
}

func (plan *DeviceRevocationPlan) RecordRemediation(
	credentialID protocol.CredentialID,
	status RemediationStatus,
) error {
	if plan == nil || !status.Valid() || !plan.known.Contains(credentialID) {
		return ErrInvalidRevocationPlan
	}
	plan.snapshot.RemediationByCredential[credentialID] = status
	if status == RemediationCompleted {
		plan.required.remove(credentialID)
	}
	// A later non-completed attempt re-opens the safety obligation. This avoids
	// treating a stale success as proof for a new failed/unknown attempt.
	if status != RemediationCompleted {
		plan.required.add(credentialID)
	}
	plan.snapshot.ExternalRemediationStatus = RemediationCompleted
	if plan.required.Len() != 0 {
		plan.snapshot.ExternalRemediationStatus = RemediationPending
		for _, value := range plan.snapshot.RemediationByCredential {
			if value == RemediationFailed {
				plan.snapshot.ExternalRemediationStatus = RemediationFailed
				break
			}
			if value == RemediationUnknown {
				plan.snapshot.ExternalRemediationStatus = RemediationUnknown
			}
		}
	}
	return nil
}

func (plan *DeviceRevocationPlan) Snapshot() RevocationSnapshot {
	if plan == nil {
		return RevocationSnapshot{}
	}
	result := plan.snapshot
	result.KnownCredentialSet = plan.known.IDs()
	result.FutureAccessBlockedSet = plan.blocked.IDs()
	result.RemediationRequiredSet = plan.required.IDs()
	result.RemediationByCredential = make(map[protocol.CredentialID]RemediationStatus)
	for key, value := range plan.snapshot.RemediationByCredential {
		result.RemediationByCredential[key] = value
	}
	return result
}

func deviceBytesZero(value []byte) bool {
	var accumulator byte
	for _, item := range value {
		accumulator |= item
	}
	return accumulator == 0
}
