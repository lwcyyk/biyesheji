param([ValidatePattern('^[A-Za-z0-9_-]+$')][string]$RunId='pair_new')
$ErrorActionPreference='Stop'
$auditRoot=$PSScriptRoot
$env:GOROOT=Join-Path $auditRoot 'toolchain\go'
$env:PATH=(Join-Path $env:GOROOT 'bin')+';'+$env:PATH
$env:GOCACHE=Join-Path $auditRoot '.gocache';$env:GOTMPDIR=Join-Path $auditRoot '.gotmp'
$env:GOMODCACHE=Join-Path $auditRoot '.gomodcache';$env:GOPATH=Join-Path $auditRoot '.gopath'
$env:GOENV='off';$env:GOTOOLCHAIN='local';$env:GOPROXY='off';$env:GOSUMDB='off';$env:GOMAXPROCS='4'
$env:TEMP=Join-Path $auditRoot '.runtmp';$env:TMP=$env:TEMP
$env:CI01_CASES=Join-Path $auditRoot 'INPUT_CASES.json'
$auditGo=Join-Path $env:GOROOT 'bin\go.exe'
foreach($variant in @('baseline','fixed')){
 $out=Join-Path $auditRoot "raw\$RunId`_$variant"
 if(Test-Path -LiteralPath $out){throw 'Use a new run ID; raw results are retained.'}
 New-Item -ItemType Directory -Path $out | Out-Null
 $env:CI01_OUTPUT=$out
 $snapshot=Join-Path $out 'source_snapshot';New-Item -ItemType Directory -Path $snapshot | Out-Null
 $hashes=@()
 foreach($relative in @('routers/authz_filter.go','routers/base.go','routers/ci01_chain_test.go','controllers/user.go','controllers/account.go','object/application.go','object/token.go','object/ci01_audit_io.go','ci01audit/audit.go','go.mod','go.sum')){
  $source=Join-Path (Join-Path $auditRoot $variant) $relative
  $target=Join-Path $snapshot $relative
  New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
  Copy-Item -LiteralPath $source -Destination $target
  $hashes+=@{path=$relative;sha256=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLower()}
 }
 $hashes | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $out 'source_hashes.json') -Encoding utf8
 Push-Location (Join-Path $auditRoot $variant)
 try {
  & $auditGo env -json GOROOT GOVERSION GOOS GOARCH GOPROXY GOSUMDB CGO_ENABLED > (Join-Path $out 'go-env.json')
  & $auditGo test -p=4 -tags=ci01audit -run '^TestCI01FullPermissionChain$' -count=1 -timeout=180s -json ./routers 1> (Join-Path $out 'go-test.jsonl') 2> (Join-Path $out 'stderr.txt')
  $exitCode=$LASTEXITCODE
  $exitCode | Set-Content -LiteralPath (Join-Path $out 'exit_code.txt') -Encoding utf8
  Write-Output "$variant exit=$exitCode"
  if($exitCode -ne 0){Get-Content -LiteralPath (Join-Path $out 'stderr.txt') -Tail 15}
 } finally {Pop-Location}
}
