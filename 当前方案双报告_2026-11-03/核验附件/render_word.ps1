$ErrorActionPreference = 'Stop'
$reportRoot = 'D:\毕业设计\当前方案双报告_2026-11-03'
$qaRoot = Join-Path $reportRoot '工作底稿\qa'
New-Item -ItemType Directory -Path $qaRoot -Force | Out-Null
$wordApp = $null
try {
  $wordApp = New-Object -ComObject Word.Application
  $wordApp.Visible = $false
  $wordApp.DisplayAlerts = 0
  foreach ($pair in @(@('当前方案_系统性调研报告_2026-11-03.docx','survey'),@('当前方案_研究与技术方案报告书_2026-11-03.docx','technical'))) {
    $wordDoc = $null
    try {
      $docPath = Join-Path $reportRoot $pair[0]
      $pdfPath = Join-Path $qaRoot ($pair[1]+'.pdf')
      $wordDoc = $wordApp.Documents.Open($docPath,$false,$true,$false)
      $null = $wordDoc.Fields.Update()
      $wordDoc.Repaginate()
      $pages = $wordDoc.ComputeStatistics(2)
      $wordDoc.ExportAsFixedFormat($pdfPath,17)
      Write-Output ($pair[1]+' pages='+$pages)
    } finally {
      if ($null -ne $wordDoc) { $wordDoc.Close(0); $null=[System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($wordDoc) }
    }
  }
} finally {
  if ($null -ne $wordApp) { $wordApp.Quit(0); $null=[System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($wordApp) }
}

