$ErrorActionPreference = 'Stop'
$taskOut = 'D:\毕业设计\研究\当前与四阶段及密码学融合_2026-11-02'
$sourceDoc = Join-Path $taskOut '认证语义与凭据配置_四阶段及密码学融合总稿_v1.0.docx'
$targetPdf = Join-Path $taskOut '工作文件\融合总稿_版面核验.pdf'
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
