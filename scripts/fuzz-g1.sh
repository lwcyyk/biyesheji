#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
FUZZ_TIME=${FUZZ_TIME:-1s}
cd "$PROJECT_ROOT"

run_fuzz() {
  package=$1
  target=$2
  go test -run='^$' -fuzz="^${target}$" -fuzztime="$FUZZ_TIME" "$package"
}

run_fuzz ./internal/protocol FuzzParseNamespaceID
run_fuzz ./internal/protocol FuzzParseCredentialID
run_fuzz ./internal/protocol FuzzVerifySigInput
run_fuzz ./internal/protocol FuzzValidateDeterministic
run_fuzz ./internal/protocol FuzzUnmarshalDeterministic
run_fuzz ./internal/cryptokit FuzzEncodeExact
run_fuzz ./internal/cryptokit FuzzParseAndOpenEventEnvelope
run_fuzz ./internal/cryptokit FuzzParseAndDecryptField
run_fuzz ./internal/cryptokit FuzzOpenHPKE
run_fuzz ./internal/cryptokit FuzzParseRootCapsule
run_fuzz ./internal/cryptokit FuzzParseRecoveryCapsule
run_fuzz ./internal/credential/domain FuzzNormalizeOrigin
run_fuzz ./internal/operation/domain FuzzParseAndVerifyDeviceOperationCredential
run_fuzz ./internal/rotation/domain FuzzNewPasswordPolicy
run_fuzz ./internal/rotation/domain FuzzPolicyEncode

echo "g1-fuzz-ok"
