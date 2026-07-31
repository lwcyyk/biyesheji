package domain

import (
	"bytes"
	"crypto/sha256"
	"errors"
	"sort"

	"vdns.local/vdns/internal/cryptokit"
	"vdns.local/vdns/internal/protocol"
)

var (
	ErrInvalidRollover    = errors.New("invalid secret generation rollover")
	ErrRolloverRecipient  = errors.New("invalid secret generation recipient")
	ErrRolloverTransition = errors.New("invalid secret generation rollover transition")
)

type DeviceStatus uint8

const (
	DeviceActive DeviceStatus = iota + 1
	DeviceSuspended
	DeviceRevoked
)

func (status DeviceStatus) Valid() bool {
	return status >= DeviceActive && status <= DeviceRevoked
}

type RolloverDevice struct {
	DeviceID      protocol.DeviceID
	HPKEPublicKey cryptokit.HPKEPublicKey
	Status        DeviceStatus
}

type RolloverStatus uint8

const (
	RolloverPrepared RolloverStatus = iota + 1
	RolloverEnvelopesCreated
	RolloverFinalSequenceAccepted
	RolloverActive
)

type RolloverRecipient struct {
	DeviceID      protocol.DeviceID
	HPKEPublicKey cryptokit.HPKEPublicKey
	EnvelopeHash  *[sha256.Size]byte
}

type GenerationRollover struct {
	namespaceID   protocol.NamespaceID
	revokedDevice protocol.DeviceID
	oldGeneration uint64
	newGeneration uint64
	status        RolloverStatus
	recipients    []RolloverRecipient
	finalSequence *uint64
}

func NewGenerationRollover(
	namespaceID protocol.NamespaceID,
	oldGeneration uint64,
	revokedDevice protocol.DeviceID,
	devices []RolloverDevice,
) (*GenerationRollover, error) {
	if allZero(namespaceID[:]) || oldGeneration == 0 ||
		allZero(revokedDevice[:]) || len(devices) < 2 {
		return nil, ErrInvalidRollover
	}
	seen := make(map[protocol.DeviceID]struct{}, len(devices))
	revokedFound := false
	recipients := make([]RolloverRecipient, 0, len(devices)-1)
	for _, device := range devices {
		if allZero(device.DeviceID[:]) || !device.Status.Valid() {
			return nil, ErrRolloverRecipient
		}
		if _, duplicate := seen[device.DeviceID]; duplicate {
			return nil, ErrRolloverRecipient
		}
		seen[device.DeviceID] = struct{}{}
		if device.DeviceID == revokedDevice {
			revokedFound = device.Status == DeviceRevoked
			continue
		}
		if device.Status != DeviceActive {
			continue
		}
		if _, err := cryptokit.ParseHPKEPublicKey(device.HPKEPublicKey[:]); err != nil {
			return nil, ErrRolloverRecipient
		}
		recipients = append(recipients, RolloverRecipient{
			DeviceID: device.DeviceID, HPKEPublicKey: device.HPKEPublicKey,
		})
	}
	if !revokedFound || len(recipients) == 0 {
		return nil, ErrRolloverRecipient
	}
	sort.Slice(recipients, func(i, j int) bool {
		return bytes.Compare(recipients[i].DeviceID[:], recipients[j].DeviceID[:]) < 0
	})
	return &GenerationRollover{
		namespaceID: namespaceID, revokedDevice: revokedDevice,
		oldGeneration: oldGeneration, newGeneration: oldGeneration + 1,
		status: RolloverPrepared, recipients: recipients,
	}, nil
}

func (rollover *GenerationRollover) Recipients() []RolloverRecipient {
	if rollover == nil {
		return nil
	}
	return cloneRolloverRecipients(rollover.recipients)
}

func (rollover *GenerationRollover) NewGeneration() uint64 {
	if rollover == nil {
		return 0
	}
	return rollover.newGeneration
}

func (rollover *GenerationRollover) Status() RolloverStatus {
	if rollover == nil {
		return 0
	}
	return rollover.status
}

func (rollover *GenerationRollover) AttachEnvelope(
	deviceID protocol.DeviceID,
	envelopeHash [sha256.Size]byte,
) error {
	if rollover == nil || rollover.status != RolloverPrepared ||
		allZero(envelopeHash[:]) || deviceID == rollover.revokedDevice {
		return ErrRolloverTransition
	}
	for index := range rollover.recipients {
		if rollover.recipients[index].DeviceID != deviceID {
			continue
		}
		if rollover.recipients[index].EnvelopeHash != nil {
			if *rollover.recipients[index].EnvelopeHash == envelopeHash {
				return nil
			}
			return ErrRolloverTransition
		}
		value := envelopeHash
		rollover.recipients[index].EnvelopeHash = &value
		for _, recipient := range rollover.recipients {
			if recipient.EnvelopeHash == nil {
				return nil
			}
		}
		rollover.status = RolloverEnvelopesCreated
		return nil
	}
	return ErrRolloverRecipient
}

func (rollover *GenerationRollover) AcceptFinalSequence(
	finalSequence uint64,
) error {
	if rollover == nil || rollover.status != RolloverEnvelopesCreated ||
		finalSequence == 0 {
		return ErrRolloverTransition
	}
	rollover.status = RolloverFinalSequenceAccepted
	rollover.finalSequence = &finalSequence
	return nil
}

func (rollover *GenerationRollover) Activate() error {
	if rollover == nil || rollover.status != RolloverFinalSequenceAccepted ||
		rollover.finalSequence == nil {
		return ErrRolloverTransition
	}
	rollover.status = RolloverActive
	return nil
}

func cloneRolloverRecipients(
	input []RolloverRecipient,
) []RolloverRecipient {
	result := append([]RolloverRecipient(nil), input...)
	for index := range result {
		result[index].EnvelopeHash = cloneHash(result[index].EnvelopeHash)
	}
	return result
}
