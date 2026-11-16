# FROZEN FUTURE COMMAND ONLY. R24 authorizes no dynamic execution.
$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
Set-Location -LiteralPath 'D:\毕业设计\auth-lifecycle'
# New-Item fails on an existing root, preserving all earlier command logs.
New-Item -ItemType Directory -Path 'D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r24\verification_runs' -ErrorAction Stop | Out-Null
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B 'D:\毕业设计\auth-lifecycle\scripts\run_dsat_authority_live_lifecycle_tests.py' --suite new54 --output-root 'D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r24\verification_runs' 1> 'D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r24\verification_runs\COMMAND_new54_stdout.log' 2> 'D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r24\verification_runs\COMMAND_new54_stderr.log'
# Read/copy $LASTEXITCODE as the actual result; this file contains no retry.
