param(
    [Parameter(Mandatory=$true)][string]$BatchRoot,
    [Parameter(Mandatory=$true)][string]$AuthorizationId,
    [string]$PythonExe = 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe',
    [switch]$Development
)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = Join-Path $repoRoot 'src'
$env:PYTHONDONTWRITEBYTECODE = '1'
$arguments = @('-B','-X','utf8',(Join-Path $PSScriptRoot 'agent_isolation.py'),'--out',$BatchRoot,'--authorization-id',$AuthorizationId)
if ($Development) { $arguments += '--development' }
& $PythonExe @arguments
exit $LASTEXITCODE
