param([string]$DocPath, [string]$PdfPath)
$ErrorActionPreference = 'Stop'
$taskWord = $null
$taskDoc = $null
try {
    $taskWord = New-Object -ComObject Word.Application
    $taskWord.Visible = $false
    $taskWord.DisplayAlerts = 0
    $taskDoc = $taskWord.Documents.Open($DocPath, $false, $false, $false)
    $taskDoc.Repaginate()
    foreach ($taskToc in $taskDoc.TablesOfContents) { $taskToc.Update() }
    $taskDoc.Repaginate()
    foreach ($taskToc in $taskDoc.TablesOfContents) { $taskToc.UpdatePageNumbers() }
    $taskDoc.Save()
    $taskDoc.ExportAsFixedFormat($PdfPath, 17)
    Write-Output ('PAGES=' + $taskDoc.ComputeStatistics(2))
} finally {
    if ($null -ne $taskDoc) { $taskDoc.Close(0); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($taskDoc) }
    if ($null -ne $taskWord) { $taskWord.Quit(); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($taskWord) }
}
