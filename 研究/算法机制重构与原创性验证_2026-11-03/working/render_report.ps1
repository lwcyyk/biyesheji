$ErrorActionPreference = 'Stop'
$taskOut = 'D:\毕业设计\研究\算法机制重构与原创性验证_2026-11-03'
$sourceDoc = Join-Path $taskOut 'A、B与AB三项算法原创性突破及优势验证研究报告_v1.0.docx'
$targetPdf = Join-Path $taskOut 'working\report_qa.pdf'
$wordApp = $null
$wordDoc = $null
try {
    $wordApp = New-Object -ComObject Word.Application
    $wordApp.Visible = $false
    $wordApp.DisplayAlerts = 0
    $wordDoc = $wordApp.Documents.Open($sourceDoc, $false, $true, $false)
    $null = $wordDoc.Fields.Update()
    $wordDoc.ExportAsFixedFormat($targetPdf, 17)
    Write-Output $targetPdf
} finally {
    if ($null -ne $wordDoc) {
        $wordDoc.Close(0)
        $null = [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($wordDoc)
    }
    if ($null -ne $wordApp) {
        $wordApp.Quit(0)
        $null = [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($wordApp)
    }
}
