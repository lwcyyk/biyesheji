$ErrorActionPreference='Stop'
$docPath='D:\毕业设计\探索进展与创新方向_2026-11-09\AI智能体授权研究探索进展与创新方向_2026-11-09.docx'
$pdfPath='D:\毕业设计\探索进展与创新方向_2026-11-09\_build\report_qa.pdf'
$word=$null
$document=$null
try {
    $word=New-Object -ComObject Word.Application
    $word.Visible=$false
    $word.DisplayAlerts=0
    $word.AutomationSecurity=3
    $document=$word.Documents.Open($docPath,$false,$false,$false)
    $document.Repaginate()
    $document.Fields.Update() | Out-Null
    foreach ($toc in $document.TablesOfContents) { $toc.Update() }
    $document.Repaginate()
    foreach ($toc in $document.TablesOfContents) { $toc.UpdatePageNumbers() }
    $document.Save()
    $document.ExportAsFixedFormat($pdfPath,17)
    Write-Output ('PAGES='+$document.ComputeStatistics(2))
    Write-Output ('PDF='+$pdfPath)
} finally {
    if ($document) { $document.Close(0) }
    if ($word -and $word.Documents.Count -eq 0) { $word.Quit() }
    if ($document) { [Runtime.InteropServices.Marshal]::ReleaseComObject($document) | Out-Null }
    if ($word) { [Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null }
}

