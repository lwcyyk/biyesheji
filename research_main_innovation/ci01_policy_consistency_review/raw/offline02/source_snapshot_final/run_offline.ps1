param([ValidatePattern('^[A-Za-z0-9_-]+$')][string]$RunId='offline_replay')
$ErrorActionPreference='Stop'
$auditRoot=$PSScriptRoot
$auditOutput=Join-Path $auditRoot "raw\$RunId"
if(Test-Path -LiteralPath $auditOutput){throw 'Use a new run identifier; raw results are retained.'}
New-Item -ItemType Directory -Path $auditOutput -Force | Out-Null
foreach($name in @('.gocache','.gotmp','.gopath')){New-Item -ItemType Directory -Path (Join-Path $auditRoot $name) -Force | Out-Null}
$env:GOCACHE=Join-Path $auditRoot '.gocache'
$env:GOTMPDIR=Join-Path $auditRoot '.gotmp'
$env:GOPATH=Join-Path $auditRoot '.gopath'
$env:GOPROXY='off'
$env:GOSUMDB='off'
$env:GOENV='off'
$env:GOTOOLCHAIN='local'
$env:AUDIT_OUTPUT=$auditOutput
$auditGo='C:\Program Files\Go\bin\go.exe'
Push-Location (Join-Path $auditRoot 'offline')
try {
    & $auditGo version | Set-Content -LiteralPath (Join-Path $auditOutput 'go-version.txt') -Encoding utf8
    & $auditGo run .\tools\extract.go 1> (Join-Path $auditOutput 'extraction_stdout.txt') 2> (Join-Path $auditOutput 'extraction_stderr.txt')
    if($LASTEXITCODE -ne 0){throw 'Verbatim extraction failed; test not run.'}
    & $auditGo test -json -count=1 ./routers 1> (Join-Path $auditOutput 'go-test.jsonl') 2> (Join-Path $auditOutput 'stderr.txt')
    $auditExit=$LASTEXITCODE
    $auditExit | Set-Content -LiteralPath (Join-Path $auditOutput 'exit_code.txt') -Encoding utf8
    Write-Output "Go test exit=$auditExit (contract mismatches remain visible; no source fix applied)."
} finally {Pop-Location}
exit $auditExit
