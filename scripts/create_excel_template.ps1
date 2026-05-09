param(
  [string]$OutputPath = 'D:\work\SOA\code\data\input\arxml_input_template.xlsx'
)

$ErrorActionPreference = 'Stop'

function Escape-XmlText {
  param([string]$Text)
  if ($null -eq $Text) { return '' }
  return [System.Security.SecurityElement]::Escape($Text)
}

function Get-ColumnName {
  param([int]$Index)
  $name = ''
  while ($Index -gt 0) {
    $mod = ($Index - 1) % 26
    $name = [char](65 + $mod) + $name
    $Index = [math]::Floor(($Index - 1) / 26)
  }
  return $name
}

$optionGroups = [ordered]@{
  ComponentCategory = @('Atomic', 'Composition')
  PackagePath = @('/ComponentTypes')
  PortInterfaceKind = @('SR', 'CS')
  PortDirection = @('R', 'P')
  DataType = @('Boolean', 'UInt8', 'UInt16', 'SInt8', 'UInt32', 'Enum')
  ComSpecType = @('NONQUEUED-RECEIVER-COM-SPEC', 'NONQUEUED-SENDER-COM-SPEC')
  ArgumentDirection = @('IN', 'OUT', 'INOUT')
  TriggerType = @('Init', 'Period', 'Invocation')
}

$sheets = @(
  @{
    Name = 'Components'
    Hidden = $false
    Headers = @('ComponentName', 'ComponentCategory', 'ComponentTypeName', 'PackagePath', 'Description')
    Rows = @(
      @('WW_ENH', 'Atomic', 'APPLICATION-SW-COMPONENT-TYPE', '/ComponentTypes', 'Example row only, replace with your real data.'),
      @('WW_ATM', 'Atomic', 'APPLICATION-SW-COMPONENT-TYPE', '/ComponentTypes', 'Example row only, replace with your real data.'),
      @('WW_TOTAL', 'Composition', 'COMPOSITION-SW-COMPONENT-TYPE', '/ComponentTypes', 'Example row only, replace with your real data.')
    )
    Validations = @(
      @{ Range = 'B2:B300'; Formula = '=Options!$A$2:$A$3' },
      @{ Range = 'C2:C300'; Formula = '"APPLICATION-SW-COMPONENT-TYPE,COMPOSITION-SW-COMPONENT-TYPE"' },
      @{ Range = 'D2:D300'; Formula = '=Options!$B$2:$B$2' }
    )
  },
  @{
    Name = 'Ports'
    Hidden = $false
    Headers = @('ComponentName', 'PortInterfaceKind', 'PortDirection', 'PortName', 'InterfaceName', 'DataElementName', 'DataType', 'InitValue', 'ComSpecType', 'OperationName', 'Description')
    Rows = @(
      @('WW_ENH', 'SR', 'R', 'VbINP_HWA_FWiperPark_flg', 'VbINP_HWA_FWiperPark_flg', 'VbINP_HWA_FWiperPark_flg', 'Boolean', '0', 'NONQUEUED-RECEIVER-COM-SPEC', '', 'Example SR input row.'),
      @('WW_ATM', 'SR', 'P', 'VbOUT_WW_FWiperLow_flg', 'VbOUT_WW_FWiperLow_flg', 'VbOUT_WW_FWiperLow_flg', 'Boolean', '0', 'NONQUEUED-SENDER-COM-SPEC', '', 'Example SR output row.'),
      @('WW_ATM', 'CS', 'P', 'rrFWiper', '', '', '', '', '', 'setFWiperCmd', 'Example CS server port row.')
    )
    Validations = @(
      @{ Range = 'B2:B1000'; Formula = '=Options!$C$2:$C$3' },
      @{ Range = 'C2:C1000'; Formula = '=Options!$D$2:$D$3' },
      @{ Range = 'G2:G1000'; Formula = '=Options!$E$2:$E$7' },
      @{ Range = 'I2:I1000'; Formula = '=Options!$F$2:$F$3' }
    )
  },
  @{
    Name = 'Arguments'
    Hidden = $false
    Headers = @('ComponentName', 'PortName', 'OperationName', 'ArgumentName', 'ArgumentType', 'ArgumentDirection', 'Description')
    Rows = @(
      @('WW_ATM', 'rrFWiper', 'setFWiperCmd', 'FWiperCmd', 'Enum', 'IN', 'Example operation input argument.'),
      @('WW_ATM', 'rrFWiper', 'setFWiperCmd', 'ReturnCode', 'Enum', 'OUT', 'Example operation return argument.')
    )
    Validations = @(
      @{ Range = 'E2:E1000'; Formula = '=Options!$E$2:$E$7' },
      @{ Range = 'F2:F1000'; Formula = '=Options!$G$2:$G$4' }
    )
  },
  @{
    Name = 'ValueMap'
    Hidden = $false
    Headers = @('TypeName', 'RawValue', 'TextValue', 'Comment')
    Rows = @(
      @('Boolean_ValidInvalid', '0', 'Invalid', 'Example row only.'),
      @('Boolean_ValidInvalid', '1', 'Valid', 'Example row only.')
    )
    Validations = @()
  },
  @{
    Name = 'Runnables'
    Hidden = $false
    Headers = @('ComponentName', 'RunnableName', 'TriggerType', 'PeriodMs', 'PortName', 'OperationName', 'Description')
    Rows = @(
      @('WW_ENH', 'WW_ENH_Init', 'Init', '', '', '', 'Example init runnable.'),
      @('WW_ENH', 'WW_ENH_Step', 'Period', '10', '', '', 'Example timing runnable.'),
      @('WW_ATM', 'rrFWiper', 'Invocation', '','rrFWiper', 'setFWiperCmd', 'Example operation-invoked runnable.')
    )
    Validations = @(
      @{ Range = 'C2:C1000'; Formula = '=Options!$H$2:$H$4' }
    )
  },
  @{
    Name = 'Options'
    Hidden = $true
    Headers = @('ComponentCategory','PackagePath','PortInterfaceKind','PortDirection','DataType','ComSpecType','ArgumentDirection','TriggerType')
    Rows = @()
    Validations = @()
  }
)

for ($i = 0; $i -lt ($optionGroups.Keys.Count | Measure-Object).Count; $i++) {
  $key = @($optionGroups.Keys)[$i]
  $values = $optionGroups[$key]
  for ($r = 0; $r -lt $values.Count; $r++) {
    if ($sheets[5].Rows.Count -le $r) {
      $sheets[5].Rows += ,(@('','','','','','','',''))
    }
    $sheets[5].Rows[$r][$i] = $values[$r]
  }
}

$sharedStrings = New-Object System.Collections.Generic.List[string]
$sharedIndex = @{}

function Get-SharedStringIndex {
  param([string]$Text)
  if (-not $sharedIndex.ContainsKey($Text)) {
    $sharedIndex[$Text] = $sharedStrings.Count
    $sharedStrings.Add($Text)
  }
  return $sharedIndex[$Text]
}

foreach ($sheet in $sheets) {
  foreach ($cell in $sheet.Headers) {
    [void](Get-SharedStringIndex $cell)
  }
  foreach ($row in $sheet.Rows) {
    foreach ($cell in $row) {
      [void](Get-SharedStringIndex ([string]$cell))
    }
  }
}

$tempRoot = Join-Path $env:TEMP ('arxml_xlsx_' + [guid]::NewGuid().ToString('N'))
$null = New-Item -ItemType Directory -Path $tempRoot
$null = New-Item -ItemType Directory -Path (Join-Path $tempRoot '_rels')
$null = New-Item -ItemType Directory -Path (Join-Path $tempRoot 'docProps')
$null = New-Item -ItemType Directory -Path (Join-Path $tempRoot 'xl')
$null = New-Item -ItemType Directory -Path (Join-Path $tempRoot 'xl\_rels')
$null = New-Item -ItemType Directory -Path (Join-Path $tempRoot 'xl\worksheets')

$contentTypes = @(
  '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
  '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
  '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
  '  <Default Extension="xml" ContentType="application/xml"/>',
  '  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
  '  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>',
  '  <Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>',
  '  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>',
  '  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
)
for ($i = 1; $i -le $sheets.Count; $i++) {
  $contentTypes += "  <Override PartName=`"/xl/worksheets/sheet$i.xml`" ContentType=`"application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml`"/>"
}
$contentTypes += '</Types>'
Set-Content -LiteralPath (Join-Path $tempRoot '[Content_Types].xml') -Value ($contentTypes -join "`r`n") -Encoding UTF8

$rootRels = @(
  '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
  '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
  '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>',
  '  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>',
  '  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>',
  '</Relationships>'
)
Set-Content -LiteralPath (Join-Path $tempRoot '_rels\.rels') -Value ($rootRels -join "`r`n") -Encoding UTF8

$appXml = @(
  '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
  '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">',
  '  <Application>Codex</Application>',
  '  <HeadingPairs><vt:vector size="2" baseType="variant"><vt:variant><vt:lpstr>Worksheets</vt:lpstr></vt:variant><vt:variant><vt:i4>6</vt:i4></vt:variant></vt:vector></HeadingPairs>',
  "  <TitlesOfParts><vt:vector size=`"$($sheets.Count)`" baseType=`"lpstr`">"
)
foreach ($sheet in $sheets) { $appXml += "    <vt:lpstr>$($sheet.Name)</vt:lpstr>" }
$appXml += '  </vt:vector></TitlesOfParts>'
$appXml += '</Properties>'
Set-Content -LiteralPath (Join-Path $tempRoot 'docProps\app.xml') -Value ($appXml -join "`r`n") -Encoding UTF8

$created = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$coreXml = @(
  '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
  '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">',
  '  <dc:creator>Codex</dc:creator>',
  '  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>',
  "  <dcterms:created xsi:type=`"dcterms:W3CDTF`">$created</dcterms:created>",
  "  <dcterms:modified xsi:type=`"dcterms:W3CDTF`">$created</dcterms:modified>",
  '</cp:coreProperties>'
)
Set-Content -LiteralPath (Join-Path $tempRoot 'docProps\core.xml') -Value ($coreXml -join "`r`n") -Encoding UTF8

$workbookXml = @(
  '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
  '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">',
  '  <sheets>'
)
for ($i = 1; $i -le $sheets.Count; $i++) {
  $state = if ($sheets[$i-1].Hidden) { ' state="hidden"' } else { '' }
  $workbookXml += "    <sheet name=`"$($sheets[$i-1].Name)`" sheetId=`"$i`"$state r:id=`"rId$i`"/>"
}
$workbookXml += '  </sheets>'
$workbookXml += '</workbook>'
Set-Content -LiteralPath (Join-Path $tempRoot 'xl\workbook.xml') -Value ($workbookXml -join "`r`n") -Encoding UTF8

$wbRels = @(
  '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
  '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
)
for ($i = 1; $i -le $sheets.Count; $i++) {
  $wbRels += "  <Relationship Id=`"rId$i`" Type=`"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet`" Target=`"worksheets/sheet$i.xml`"/>"
}
$wbRels += "  <Relationship Id=`"rId$($sheets.Count + 1)`" Type=`"http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles`" Target=`"styles.xml`"/>"
$wbRels += "  <Relationship Id=`"rId$($sheets.Count + 2)`" Type=`"http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings`" Target=`"sharedStrings.xml`"/>"
$wbRels += '</Relationships>'
Set-Content -LiteralPath (Join-Path $tempRoot 'xl\_rels\workbook.xml.rels') -Value ($wbRels -join "`r`n") -Encoding UTF8

$stylesXml = @(
  '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
  '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
  '  <fonts count="2">',
  '    <font><sz val="11"/><name val="Calibri"/></font>',
  '    <font><b/><sz val="11"/><name val="Calibri"/></font>',
  '  </fonts>',
  '  <fills count="2">',
  '    <fill><patternFill patternType="none"/></fill>',
  '    <fill><patternFill patternType="gray125"/></fill>',
  '  </fills>',
  '  <borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>',
  '  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>',
  '  <cellXfs count="2">',
  '    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>',
  '    <xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>',
  '  </cellXfs>',
  '  <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>',
  '</styleSheet>'
)
Set-Content -LiteralPath (Join-Path $tempRoot 'xl\styles.xml') -Value ($stylesXml -join "`r`n") -Encoding UTF8

$sharedXml = @(
  '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
  "<sst xmlns=`"http://schemas.openxmlformats.org/spreadsheetml/2006/main`" count=`"$($sharedStrings.Count)`" uniqueCount=`"$($sharedStrings.Count)`">"
)
foreach ($text in $sharedStrings) {
  $sharedXml += "  <si><t>$(Escape-XmlText $text)</t></si>"
}
$sharedXml += '</sst>'
Set-Content -LiteralPath (Join-Path $tempRoot 'xl\sharedStrings.xml') -Value ($sharedXml -join "`r`n") -Encoding UTF8

for ($sheetIndex = 0; $sheetIndex -lt $sheets.Count; $sheetIndex++) {
  $sheet = $sheets[$sheetIndex]
  $lines = @(
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
    '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
    '  <sheetViews><sheetView workbookViewId="0"/></sheetViews>',
    '  <sheetFormatPr defaultRowHeight="15"/>',
    '  <sheetData>'
  )
  $allRows = New-Object System.Collections.ArrayList
  [void]$allRows.Add($sheet.Headers)
  foreach ($sheetRow in $sheet.Rows) {
    [void]$allRows.Add($sheetRow)
  }
  for ($r = 0; $r -lt $allRows.Count; $r++) {
    $rowNum = $r + 1
    $lines += "    <row r=`"$rowNum`">"
    $row = $allRows[$r]
    for ($c = 0; $c -lt $row.Count; $c++) {
      $colNum = $c + 1
      $ref = "$(Get-ColumnName $colNum)$rowNum"
      $idx = Get-SharedStringIndex ([string]$row[$c])
      $style = if ($rowNum -eq 1) { ' s="1"' } else { '' }
      $lines += "      <c r=`"$ref`" t=`"s`"$style><v>$idx</v></c>"
    }
    $lines += '    </row>'
  }
  $lines += '  </sheetData>'
  if ($sheet.Validations.Count -gt 0) {
    $lines += "  <dataValidations count=`"$($sheet.Validations.Count)`">"
    foreach ($validation in $sheet.Validations) {
      $formula = Escape-XmlText $validation.Formula
      $lines += "    <dataValidation type=`"list`" allowBlank=`"1`" showDropDown=`"0`" sqref=`"$($validation.Range)`"><formula1>$formula</formula1></dataValidation>"
    }
    $lines += '  </dataValidations>'
  }
  $lines += '</worksheet>'
  Set-Content -LiteralPath (Join-Path $tempRoot ("xl\worksheets\sheet{0}.xml" -f ($sheetIndex + 1))) -Value ($lines -join "`r`n") -Encoding UTF8
}

$zipPath = [IO.Path]::ChangeExtension($OutputPath, '.zip')
if (Test-Path -LiteralPath $zipPath) { Remove-Item -LiteralPath $zipPath -Force }
if (Test-Path -LiteralPath $OutputPath) { Remove-Item -LiteralPath $OutputPath -Force }
Compress-Archive -Path (Join-Path $tempRoot '*') -DestinationPath $zipPath -Force
Move-Item -LiteralPath $zipPath -Destination $OutputPath -Force
Remove-Item -LiteralPath $tempRoot -Recurse -Force

Write-Output "CREATED`t$OutputPath"
