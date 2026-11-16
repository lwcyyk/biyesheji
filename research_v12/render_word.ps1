$ErrorActionPreference = 'Stop'
$base = $PSScriptRoot
$inputDoc = Join-Path $base 'A、B与AB结构性算法深化及动态核心传递验证研究报告_v1.2.docx'
$qa = Join-Path $base 'qa'
New-Item -ItemType Directory -Path $qa -Force | Out-Null
$outputPdf = Join-Path $qa 'report.pdf'
$word = New-Object -ComObject Word.Application
if ($word.Documents.Count -ne 0) { throw 'Automation instance already has documents; refusing to touch them.' }
$word.Visible = $false
$word.DisplayAlerts = 0
$word.AutomationSecurity = 3
$opened = $null
try {
    $opened = $word.Documents.Open($inputDoc, $false, $true, $false)
    $opened.ExportAsFixedFormat($outputPdf, 17)
    Write-Output $outputPdf
} finally {
    if ($null -ne $opened) { $opened.Close(0) }
    $word.Quit()
}
