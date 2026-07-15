param(
    [string]$SourcePath = "",
    [string]$OutputPath = "docs/signal_delivery_template_v1.1.docx"
)

$ErrorActionPreference = "Stop"

function Escape-Xml([string]$Text) {
    if ($null -eq $Text) { return "" }
    return [System.Security.SecurityElement]::Escape($Text)
}

function WpText([string]$Text, [bool]$Bold = $false, [int]$FontSize = 21) {
    $escaped = Escape-Xml $Text
    $boldXml = if ($Bold) { "<w:b/>" } else { "" }
    return "<w:r><w:rPr>$boldXml<w:sz w:val=""$FontSize""/><w:szCs w:val=""$FontSize""/></w:rPr><w:t xml:space=""preserve"">$escaped</w:t></w:r>"
}

function Para([string]$Text, [string]$Style = "Normal", [bool]$Bold = $false) {
    $styleXml = if ($Style) { "<w:pPr><w:pStyle w:val=""$Style""/></w:pPr>" } else { "" }
    $size = if ($Style -eq "Title") { 32 } elseif ($Style -eq "Heading1") { 28 } elseif ($Style -eq "Heading2") { 24 } else { 21 }
    return "<w:p>$styleXml$(WpText $Text $Bold $size)</w:p>"
}

function Bullet([string]$Text) {
    return "<w:p><w:pPr><w:pStyle w:val=""ListParagraph""/><w:numPr><w:ilvl w:val=""0""/><w:numId w:val=""1""/></w:numPr></w:pPr>$(WpText $Text $false 21)</w:p>"
}

function TableXml($Rows) {
    if ($Rows.Count -eq 0) { return "" }
    $maxCols = 0
    foreach ($row in $Rows) {
        if ($row.Count -gt $maxCols) { $maxCols = $row.Count }
    }

    $xml = "<w:tbl><w:tblPr><w:tblStyle w:val=""TableGrid""/><w:tblW w:w=""0"" w:type=""auto""/><w:tblLook w:val=""04A0"" w:firstRow=""1"" w:lastRow=""0"" w:firstColumn=""1"" w:lastColumn=""0"" w:noHBand=""0"" w:noVBand=""1""/></w:tblPr><w:tblGrid>"
    for ($i = 0; $i -lt $maxCols; $i++) { $xml += "<w:gridCol w:w=""1800""/>" }
    $xml += "</w:tblGrid>"

    for ($r = 0; $r -lt $Rows.Count; $r++) {
        $xml += "<w:tr>"
        $row = $Rows[$r]
        for ($c = 0; $c -lt $maxCols; $c++) {
            $text = if ($c -lt $row.Count) { $row[$c] } else { "" }
            $shd = if ($r -eq 0) { "<w:shd w:fill=""D9EAF7""/>" } else { "" }
            $cellPara = Para $text $null ($r -eq 0)
            $xml += "<w:tc><w:tcPr>$shd<w:tcW w:w=""1800"" w:type=""dxa""/></w:tcPr>$cellPara</w:tc>"
        }
        $xml += "</w:tr>"
    }

    $xml += "</w:tbl>"
    return $xml
}

function Is-MarkdownSeparator([string]$Line) {
    $trim = $Line.Trim()
    if (-not $trim.StartsWith("|")) { return $false }
    $parts = $trim.Trim("|").Split("|")
    foreach ($part in $parts) {
        if (($part.Trim() -replace "[:-]", "") -ne "") { return $false }
    }
    return $true
}

function Parse-TableRow([string]$Line) {
    return @($Line.Trim().Trim("|").Split("|") | ForEach-Object { $_.Trim() })
}

$repoRoot = (Resolve-Path ".").Path
if ($SourcePath -eq "") {
    $docsDir = Join-Path $repoRoot "docs"
    $sourceCandidate = Get-ChildItem -Path $docsDir -Filter "*_v1.1.md" | Select-Object -First 1
    if ($null -eq $sourceCandidate) {
        throw "No *_v1.1.md source template found under docs."
    }
    $sourceFullPath = $sourceCandidate.FullName
} else {
    $sourceFullPath = Join-Path $repoRoot $SourcePath
}
$resolvedOutput = Join-Path $repoRoot $OutputPath

$utf8 = New-Object System.Text.UTF8Encoding($false)
$lines = [System.IO.File]::ReadAllLines($sourceFullPath, $utf8)

$content = ""
$i = 0
while ($i -lt $lines.Count) {
    $line = $lines[$i]
    $trim = $line.Trim()

    if ($trim -eq "") {
        $i++
        continue
    }

    if ($trim.StartsWith("|")) {
        $rows = New-Object System.Collections.ArrayList
        while ($i -lt $lines.Count -and $lines[$i].Trim().StartsWith("|")) {
            if (-not (Is-MarkdownSeparator $lines[$i])) {
                [void]$rows.Add((Parse-TableRow $lines[$i]))
            }
            $i++
        }
        $content += TableXml $rows
        continue
    }

    if ($trim.StartsWith("# ")) {
        $content += Para $trim.Substring(2).Trim() "Title" $true
    } elseif ($trim.StartsWith("## ")) {
        $content += Para $trim.Substring(3).Trim() "Heading1" $true
    } elseif ($trim.StartsWith("### ")) {
        $content += Para $trim.Substring(4).Trim() "Heading2" $true
    } elseif ($trim.StartsWith("- ")) {
        $content += Bullet $trim.Substring(2).Trim()
    } elseif ($trim.StartsWith("> ")) {
        $content += Para $trim.Substring(2).Trim() "Normal" $false
    } else {
        $content += Para $trim "Normal" $false
    }

    $i++
}

$documentXml = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:w10="urn:schemas-microsoft-com:office:word" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" mc:Ignorable="w14 wp14">
  <w:body>
    $content
    <w:sectPr><w:pgSz w:w="16838" w:h="11906" w:orient="landscape"/><w:pgMar w:top="720" w:right="720" w:bottom="720" w:left="720" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>
  </w:body>
</w:document>
"@

$stylesXml = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>
  <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:qFormat/><w:rPr><w:b/><w:sz w:val="32"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:rPr><w:b/><w:sz w:val="28"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:rPr><w:b/><w:sz w:val="24"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="ListParagraph"><w:name w:val="List Paragraph"/><w:basedOn w:val="Normal"/><w:qFormat/><w:pPr><w:ind w:left="720"/></w:pPr></w:style>
  <w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/><w:basedOn w:val="TableNormal"/><w:uiPriority w:val="59"/><w:semiHidden/><w:unhideWhenUsed/><w:tblPr><w:tblBorders><w:top w:val="single" w:sz="4" w:space="0" w:color="auto"/><w:left w:val="single" w:sz="4" w:space="0" w:color="auto"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="auto"/><w:right w:val="single" w:sz="4" w:space="0" w:color="auto"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="auto"/><w:insideV w:val="single" w:sz="4" w:space="0" w:color="auto"/></w:tblBorders></w:tblPr></w:style>
</w:styles>
"@

$numberingXml = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:abstractNum w:abstractNumId="0"><w:multiLevelType w:val="hybridMultilevel"/><w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="•"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr></w:lvl></w:abstractNum>
  <w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
</w:numbering>
"@

$contentTypesXml = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
</Types>
"@

$relsXml = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"@

$docRelsXml = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
</Relationships>
"@

$outputDir = Split-Path -Parent $resolvedOutput
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

$buildDir = Join-Path $env:TEMP "generate_arxml_signal_template_docx"
if (Test-Path $buildDir) { Remove-Item -LiteralPath $buildDir -Recurse -Force }
New-Item -ItemType Directory -Force -Path (Join-Path $buildDir "_rels") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $buildDir "word/_rels") | Out-Null

$utf8Bom = New-Object System.Text.UTF8Encoding($true)
[System.IO.File]::WriteAllText((Join-Path $buildDir "[Content_Types].xml"), $contentTypesXml, $utf8Bom)
[System.IO.File]::WriteAllText((Join-Path $buildDir "_rels/.rels"), $relsXml, $utf8Bom)
[System.IO.File]::WriteAllText((Join-Path $buildDir "word/document.xml"), $documentXml, $utf8Bom)
[System.IO.File]::WriteAllText((Join-Path $buildDir "word/styles.xml"), $stylesXml, $utf8Bom)
[System.IO.File]::WriteAllText((Join-Path $buildDir "word/numbering.xml"), $numberingXml, $utf8Bom)
[System.IO.File]::WriteAllText((Join-Path $buildDir "word/_rels/document.xml.rels"), $docRelsXml, $utf8Bom)

if (Test-Path $resolvedOutput) { Remove-Item -LiteralPath $resolvedOutput -Force }
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [System.IO.Compression.ZipFile]::Open($resolvedOutput, [System.IO.Compression.ZipArchiveMode]::Create)
try {
    [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive, (Join-Path $buildDir "[Content_Types].xml"), "[Content_Types].xml") | Out-Null
    [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive, (Join-Path $buildDir "_rels/.rels"), "_rels/.rels") | Out-Null
    [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive, (Join-Path $buildDir "word/document.xml"), "word/document.xml") | Out-Null
    [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive, (Join-Path $buildDir "word/styles.xml"), "word/styles.xml") | Out-Null
    [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive, (Join-Path $buildDir "word/numbering.xml"), "word/numbering.xml") | Out-Null
    [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive, (Join-Path $buildDir "word/_rels/document.xml.rels"), "word/_rels/document.xml.rels") | Out-Null
} finally {
    $archive.Dispose()
}

Write-Host "Created $resolvedOutput"
