$ErrorActionPreference = 'Stop'
$taskOut = 'D:\毕业设计\研究\主线与密码学机制融合_2026-11-03'
$sourceDoc = Join-Path $taskOut 'A、B与AB三项算法研究报告_v1.1_密码学机制融合版.docx'
$targetPdf = Join-Path $taskOut 'working\merged_qa.pdf'
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
