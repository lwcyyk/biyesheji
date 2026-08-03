package application

import (
	"crypto/sha256"
	"testing"
	"time"

	"vpass.local/vpass/internal/cryptokit"
	"vpass.local/vpass/internal/protocol"
)

func TestAuditScan100KUnderFiveSeconds(t *testing.T) {
	const recordCount = 100_000
	records := make([]AnalysisRecord, recordCount)
	for index := range records {
		var credentialID protocol.CredentialID
		credentialID[0] = byte(index >> 16)
		credentialID[1] = byte(index >> 8)
		credentialID[2] = byte(index)
		credentialID[31] = 1
		var witness cryptokit.ReuseTag
		witness[0] = byte(index >> 24)
		witness[1] = byte(index >> 16)
		witness[2] = byte(index >> 8)
		witness[3] = byte(index)
		witness[31] = 1
		evidence := sha256.Sum256([]byte{
			byte(index >> 24), byte(index >> 16), byte(index >> 8), byte(index),
		})
		records[index] = AnalysisRecord{
			CredentialID: credentialID, Version: 1, Epoch: 7,
			ObservedTimeBucket: 100, UpdatedTimeBucket: 100,
			Witness: witness, DeviceAuthorized: true,
			EvidenceDigests: [][sha256.Size]byte{evidence},
		}
	}
	candidate := records[recordCount/2].Witness
	started := time.Now()
	findings, err := analyzeRecords(AnalysisRequest{
		Records: records, CurrentBucket: 100, StaleAfterBucket: 90,
		AnalysisSalt: [sha256.Size]byte{1},
	}, map[uint64]cryptokit.ReuseTag{7: candidate})
	elapsed := time.Since(started)
	if err != nil {
		t.Fatal(err)
	}
	if len(findings) != 1 {
		t.Fatalf("findings=%d want=1", len(findings))
	}
	if elapsed >= 5*time.Second {
		t.Fatalf("100k scan took %s, target <5s", elapsed)
	}
	t.Logf(`{"records":%d,"elapsed_ns":%d,"findings":%d}`, recordCount, elapsed.Nanoseconds(), len(findings))
}
