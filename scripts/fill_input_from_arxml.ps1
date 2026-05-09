param(
  [string]$ArxmlPath = 'C:\Users\20261\Downloads\WW0428.arxml',
  [string]$OutputPath = 'D:\work\SOA\code\data\input\filled_from_arxml.xlsx'
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

function Get-LastPathToken {
  param([string]$PathValue)
  if ([string]::IsNullOrWhiteSpace($PathValue)) { return '' }
  $parts = $PathValue.Trim('/') -split '/'
  return $parts[-1]
}

function Get-PackagePathForNode {
  param(
    [System.Xml.XmlNode]$Node,
    [System.Xml.XmlNamespaceManager]$Ns
  )
  $names = New-Object System.Collections.Generic.List[string]
  $current = $Node.ParentNode
  while ($current) {
    if ($current.LocalName -eq 'AR-PACKAGE') {
      $sn = $current.SelectSingleNode('./a:SHORT-NAME', $Ns)
      if ($sn) { $names.Insert(0, $sn.InnerText) }
    }
    $current = $current.ParentNode
  }
  if ($names.Count -eq 0) { return '' }
  return '/' + ($names -join '/')
}

function Get-InitValueFromPort {
  param(
    [System.Xml.XmlNode]$PortNode,
    [System.Xml.XmlNamespaceManager]$Ns
  )
  $vt = $PortNode.SelectSingleNode('.//a:INIT-VALUE//a:VT', $Ns)
  if ($vt) { return $vt.InnerText }
  return ''
}

function Convert-PeriodToMs {
  param([string]$PeriodText)
  if ([string]::IsNullOrWhiteSpace($PeriodText)) { return '' }
  $value = 0.0
  if ([double]::TryParse($PeriodText, [ref]$value)) {
    if ($value -le 1) { return [int]([math]::Round($value * 1000)) }
    return [int]([math]::Round($value))
  }
  return $PeriodText
}

[xml]$xml = Get-Content -LiteralPath $ArxmlPath -Raw -Encoding UTF8
$nsUri = $xml.DocumentElement.NamespaceURI
$ns = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
$ns.AddNamespace('a', $nsUri)

$appSwcs = $xml.SelectNodes('//a:APPLICATION-SW-COMPONENT-TYPE', $ns)
$compSwcs = $xml.SelectNodes('//a:COMPOSITION-SW-COMPONENT-TYPE', $ns)

$componentsRows = New-Object System.Collections.ArrayList
foreach ($swc in $appSwcs) {
  $name = $swc.SelectSingleNode('./a:SHORT-NAME', $ns).InnerText
  $pkg = Get-PackagePathForNode -Node $swc -Ns $ns
  [void]$componentsRows.Add(@($name, 'Atomic', 'APPLICATION-SW-COMPONENT-TYPE', $pkg, ''))
}
foreach ($swc in $compSwcs) {
  $name = $swc.SelectSingleNode('./a:SHORT-NAME', $ns).InnerText
  $pkg = Get-PackagePathForNode -Node $swc -Ns $ns
  [void]$componentsRows.Add(@($name, 'Composition', 'COMPOSITION-SW-COMPONENT-TYPE', $pkg, ''))
}

$srInterfaces = @{}
foreach ($ifNode in $xml.SelectNodes('//a:SENDER-RECEIVER-INTERFACE', $ns)) {
  $ifName = $ifNode.SelectSingleNode('./a:SHORT-NAME', $ns).InnerText
  $dataElement = $ifNode.SelectSingleNode('./a:DATA-ELEMENTS/a:VARIABLE-DATA-PROTOTYPE', $ns)
  if (-not $dataElement) { continue }
  $elemName = $dataElement.SelectSingleNode('./a:SHORT-NAME', $ns).InnerText
  $typeRef = $dataElement.SelectSingleNode('./a:TYPE-TREF', $ns)
  $dataType = if ($typeRef) { Get-LastPathToken $typeRef.InnerText } else { '' }
  $srInterfaces[$ifName] = [pscustomobject]@{
    InterfaceName = $ifName
    DataElementName = $elemName
    DataType = $dataType
  }
}

$csInterfaces = @{}
foreach ($ifNode in $xml.SelectNodes('//a:CLIENT-SERVER-INTERFACE', $ns)) {
  $ifName = $ifNode.SelectSingleNode('./a:SHORT-NAME', $ns).InnerText
  $opMap = @{}
  foreach ($opNode in $ifNode.SelectNodes('./a:OPERATIONS/a:CLIENT-SERVER-OPERATION', $ns)) {
    $opName = $opNode.SelectSingleNode('./a:SHORT-NAME', $ns).InnerText
    $args = New-Object System.Collections.ArrayList
    foreach ($argNode in $opNode.SelectNodes('./a:ARGUMENTS/a:ARGUMENT-DATA-PROTOTYPE', $ns)) {
      $argTypeRef = $argNode.SelectSingleNode('./a:TYPE-TREF', $ns)
      [void]$args.Add([pscustomobject]@{
        ArgumentName = $argNode.SelectSingleNode('./a:SHORT-NAME', $ns).InnerText
        ArgumentType = $(if ($argTypeRef) { Get-LastPathToken $argTypeRef.InnerText } else { '' })
        ArgumentDirection = $(($argNode.SelectSingleNode('./a:DIRECTION', $ns)).InnerText)
      })
    }
    $opMap[$opName] = $args
  }
  $csInterfaces[$ifName] = $opMap
}

$portsRows = New-Object System.Collections.ArrayList
$argumentsRows = New-Object System.Collections.ArrayList
$usedTypes = New-Object System.Collections.Generic.HashSet[string]

foreach ($swc in $appSwcs) {
  $componentName = $swc.SelectSingleNode('./a:SHORT-NAME', $ns).InnerText
  foreach ($port in $swc.SelectNodes('./a:PORTS/*', $ns)) {
    $portName = $port.SelectSingleNode('./a:SHORT-NAME', $ns).InnerText
    $isProvider = $port.LocalName -eq 'P-PORT-PROTOTYPE'
    $portDirection = if ($isProvider) { 'P' } else { 'R' }
    $interfaceRef = $port.SelectSingleNode('./a:REQUIRED-INTERFACE-TREF|./a:PROVIDED-INTERFACE-TREF', $ns)
    $interfaceName = if ($interfaceRef) { Get-LastPathToken $interfaceRef.InnerText } else { '' }
    $dest = if ($interfaceRef) { $interfaceRef.GetAttribute('DEST') } else { '' }

    if ($dest -eq 'SENDER-RECEIVER-INTERFACE') {
      $comSpecNode = $port.SelectSingleNode('./a:REQUIRED-COM-SPECS/*|./a:PROVIDED-COM-SPECS/*', $ns)
      $comSpecType = if ($comSpecNode) { $comSpecNode.LocalName } else { '' }
      $initValue = Get-InitValueFromPort -PortNode $port -Ns $ns
      $elemName = ''
      $dataType = ''
      if ($srInterfaces.ContainsKey($interfaceName)) {
        $elemName = $srInterfaces[$interfaceName].DataElementName
        $dataType = $srInterfaces[$interfaceName].DataType
      } else {
        $dataRef = $port.SelectSingleNode('.//a:DATA-ELEMENT-REF', $ns)
        $elemName = if ($dataRef) { Get-LastPathToken $dataRef.InnerText } else { '' }
      }
      if ($dataType) { [void]$usedTypes.Add($dataType) }
      [void]$portsRows.Add(@(
        $componentName,
        'SR',
        $portDirection,
        $portName,
        $interfaceName,
        $elemName,
        $dataType,
        $initValue,
        $comSpecType,
        '',
        ''
      ))
    }
    elseif ($dest -eq 'CLIENT-SERVER-INTERFACE') {
      $comSpecNode = $port.SelectSingleNode('./a:REQUIRED-COM-SPECS/*|./a:PROVIDED-COM-SPECS/*', $ns)
      $comSpecType = if ($comSpecNode) { $comSpecNode.LocalName } else { '' }
      $opRef = $port.SelectSingleNode('.//a:OPERATION-REF', $ns)
      $opName = if ($opRef) { Get-LastPathToken $opRef.InnerText } else { '' }
      [void]$portsRows.Add(@(
        $componentName,
        'CS',
        $portDirection,
        $portName,
        $interfaceName,
        '',
        '',
        '',
        $comSpecType,
        $opName,
        ''
      ))

      if ($csInterfaces.ContainsKey($interfaceName) -and $csInterfaces[$interfaceName].ContainsKey($opName)) {
        foreach ($arg in $csInterfaces[$interfaceName][$opName]) {
          if ($arg.ArgumentType) { [void]$usedTypes.Add($arg.ArgumentType) }
          [void]$argumentsRows.Add(@(
            $componentName,
            $portName,
            $opName,
            $arg.ArgumentName,
            $arg.ArgumentType,
            $arg.ArgumentDirection,
            ''
          ))
        }
      }
    }
  }
}

$compuMethods = @{}
foreach ($cmNode in $xml.SelectNodes('//a:COMPU-METHOD[a:CATEGORY="TEXTTABLE"]', $ns)) {
  $cmName = $cmNode.SelectSingleNode('./a:SHORT-NAME', $ns).InnerText
  $rows = New-Object System.Collections.ArrayList
  foreach ($scale in $cmNode.SelectNodes('.//a:COMPU-SCALE', $ns)) {
    $raw = $scale.SelectSingleNode('./a:LOWER-LIMIT', $ns)
    $text = $scale.SelectSingleNode('./a:COMPU-CONST/a:VT', $ns)
    [void]$rows.Add(@(
      '',
      $(if ($raw) { $raw.InnerText } else { '' }),
      $(if ($text) { $text.InnerText } else { '' }),
      ''
    ))
  }
  $compuMethods[$cmName] = $rows
}

$dataTypeToCompu = @{}
foreach ($adt in $xml.SelectNodes('//a:APPLICATION-PRIMITIVE-DATA-TYPE', $ns)) {
  $dtName = $adt.SelectSingleNode('./a:SHORT-NAME', $ns).InnerText
  $cmRef = $adt.SelectSingleNode('.//a:COMPU-METHOD-REF', $ns)
  if ($cmRef) { $dataTypeToCompu[$dtName] = Get-LastPathToken $cmRef.InnerText }
}
foreach ($idt in $xml.SelectNodes('//a:IMPLEMENTATION-DATA-TYPE', $ns)) {
  $dtName = $idt.SelectSingleNode('./a:SHORT-NAME', $ns).InnerText
  $cmRef = $idt.SelectSingleNode('.//a:COMPU-METHOD-REF', $ns)
  if ($cmRef) { $dataTypeToCompu[$dtName] = Get-LastPathToken $cmRef.InnerText }
}

$valueMapRows = New-Object System.Collections.ArrayList
foreach ($typeName in ($usedTypes | Sort-Object)) {
  if (-not $dataTypeToCompu.ContainsKey($typeName)) { continue }
  $cmName = $dataTypeToCompu[$typeName]
  if (-not $compuMethods.ContainsKey($cmName)) { continue }
  foreach ($row in $compuMethods[$cmName]) {
    [void]$valueMapRows.Add(@($typeName, $row[1], $row[2], $row[3]))
  }
}

$runnableEventMap = @{}
foreach ($event in $xml.SelectNodes('//a:INIT-EVENT', $ns)) {
  $start = $event.SelectSingleNode('./a:START-ON-EVENT-REF', $ns).InnerText
  $runnableName = Get-LastPathToken $start
  $runnableEventMap[$start] = [pscustomobject]@{ TriggerType='Init'; PeriodMs=''; PortName=''; OperationName='' }
  $runnableEventMap[$runnableName] = [pscustomobject]@{ TriggerType='Init'; PeriodMs=''; PortName=''; OperationName='' }
}
foreach ($event in $xml.SelectNodes('//a:TIMING-EVENT', $ns)) {
  $start = $event.SelectSingleNode('./a:START-ON-EVENT-REF', $ns).InnerText
  $runnableName = Get-LastPathToken $start
  $period = $event.SelectSingleNode('./a:PERIOD', $ns)
  $periodMs = if ($period) { Convert-PeriodToMs $period.InnerText } else { '' }
  $info = [pscustomobject]@{ TriggerType='Period'; PeriodMs="$periodMs"; PortName=''; OperationName='' }
  $runnableEventMap[$start] = $info
  $runnableEventMap[$runnableName] = $info
}
foreach ($event in $xml.SelectNodes('//a:OPERATION-INVOKED-EVENT', $ns)) {
  $start = $event.SelectSingleNode('./a:START-ON-EVENT-REF', $ns).InnerText
  $runnableName = Get-LastPathToken $start
  $portRef = $event.SelectSingleNode('./a:OPERATION-IREF/a:CONTEXT-P-PORT-REF', $ns)
  $opRef = $event.SelectSingleNode('./a:OPERATION-IREF/a:TARGET-PROVIDED-OPERATION-REF', $ns)
  $info = [pscustomobject]@{
    TriggerType='Invocation'
    PeriodMs=''
    PortName=$(if ($portRef) { Get-LastPathToken $portRef.InnerText } else { '' })
    OperationName=$(if ($opRef) { Get-LastPathToken $opRef.InnerText } else { '' })
  }
  $runnableEventMap[$start] = $info
  $runnableEventMap[$runnableName] = $info
}

$runnablesRows = New-Object System.Collections.ArrayList
foreach ($swc in $appSwcs) {
  $componentName = $swc.SelectSingleNode('./a:SHORT-NAME', $ns).InnerText
  foreach ($rbl in $swc.SelectNodes('.//a:RUNNABLE-ENTITY', $ns)) {
    $runnableName = $rbl.SelectSingleNode('./a:SHORT-NAME', $ns).InnerText
    $runnablePath = $null
    $symbol = $rbl.SelectSingleNode('./a:SYMBOL', $ns)
    $key = $runnableName
    $eventInfo = if ($runnableEventMap.ContainsKey($key)) { $runnableEventMap[$key] } else { [pscustomobject]@{TriggerType='';PeriodMs='';PortName='';OperationName=''} }
    [void]$runnablesRows.Add(@(
      $componentName,
      $runnableName,
      $eventInfo.TriggerType,
      $eventInfo.PeriodMs,
      $eventInfo.PortName,
      $eventInfo.OperationName,
      ''
    ))
  }
}

$optionGroups = [ordered]@{
  ComponentCategory = @('Atomic', 'Composition')
  ComponentTypeName = @('APPLICATION-SW-COMPONENT-TYPE', 'COMPOSITION-SW-COMPONENT-TYPE')
  PackagePath = @('/Components', '/ComponentTypes')
  PortInterfaceKind = @('SR', 'CS')
  PortDirection = @('R', 'P')
  DataType = (($usedTypes | Sort-Object) + @('Boolean','UInt8','UInt16','SInt8','UInt32','Enum') | Select-Object -Unique)
  ComSpecType = @('NONQUEUED-RECEIVER-COM-SPEC', 'NONQUEUED-SENDER-COM-SPEC', 'CLIENT-COM-SPEC', 'SERVER-COM-SPEC')
  ArgumentDirection = @('IN', 'OUT', 'INOUT')
  TriggerType = @('Init', 'Period', 'Invocation')
}

$sheets = @(
  @{
    Name = 'Components'
    Hidden = $false
    Headers = @('ComponentName', 'ComponentCategory', 'ComponentTypeName', 'PackagePath', 'Description')
    Rows = $componentsRows
    Validations = @(
      @{ Range = 'B2:B1000'; Formula = '=Options!$A$2:$A$3' },
      @{ Range = 'C2:C1000'; Formula = '=Options!$B$2:$B$3' },
      @{ Range = 'D2:D1000'; Formula = '=Options!$C$2:$C$3' }
    )
  },
  @{
    Name = 'Ports'
    Hidden = $false
    Headers = @('ComponentName', 'PortInterfaceKind', 'PortDirection', 'PortName', 'InterfaceName', 'DataElementName', 'DataType', 'InitValue', 'ComSpecType', 'OperationName', 'Description')
    Rows = $portsRows
    Validations = @(
      @{ Range = 'B2:B2000'; Formula = '=Options!$D$2:$D$3' },
      @{ Range = 'C2:C2000'; Formula = '=Options!$E$2:$E$3' },
      @{ Range = 'G2:G2000'; Formula = '=Options!$F$2:$F$200' },
      @{ Range = 'I2:I2000'; Formula = '=Options!$G$2:$G$5' }
    )
  },
  @{
    Name = 'Arguments'
    Hidden = $false
    Headers = @('ComponentName', 'PortName', 'OperationName', 'ArgumentName', 'ArgumentType', 'ArgumentDirection', 'Description')
    Rows = $argumentsRows
    Validations = @(
      @{ Range = 'E2:E2000'; Formula = '=Options!$F$2:$F$200' },
      @{ Range = 'F2:F2000'; Formula = '=Options!$H$2:$H$4' }
    )
  },
  @{
    Name = 'ValueMap'
    Hidden = $false
    Headers = @('TypeName', 'RawValue', 'TextValue', 'Comment')
    Rows = $valueMapRows
    Validations = @()
  },
  @{
    Name = 'Runnables'
    Hidden = $false
    Headers = @('ComponentName', 'RunnableName', 'TriggerType', 'PeriodMs', 'PortName', 'OperationName', 'Description')
    Rows = $runnablesRows
    Validations = @(
      @{ Range = 'C2:C1000'; Formula = '=Options!$I$2:$I$4' }
    )
  },
  @{
    Name = 'Options'
    Hidden = $true
    Headers = @('ComponentCategory','ComponentTypeName','PackagePath','PortInterfaceKind','PortDirection','DataType','ComSpecType','ArgumentDirection','TriggerType')
    Rows = @()
    Validations = @()
  }
)

for ($i = 0; $i -lt ($optionGroups.Keys | Measure-Object).Count; $i++) {
  $key = @($optionGroups.Keys)[$i]
  $values = @($optionGroups[$key])
  for ($r = 0; $r -lt $values.Count; $r++) {
    if ($sheets[5].Rows.Count -le $r) {
      $sheets[5].Rows += ,(@('','','','','','','','',''))
    }
    $sheets[5].Rows[$r][$i] = [string]$values[$r]
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
  foreach ($cell in $sheet.Headers) { [void](Get-SharedStringIndex ([string]$cell)) }
  foreach ($row in $sheet.Rows) {
    foreach ($cell in $row) { [void](Get-SharedStringIndex ([string]$cell)) }
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
  foreach ($sheetRow in $sheet.Rows) { [void]$allRows.Add($sheetRow) }
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

if (Test-Path -LiteralPath $OutputPath) {
  $backup = Join-Path (Split-Path -Parent $OutputPath) ("input_backup_{0}.xlsx" -f (Get-Date -Format 'yyyyMMdd_HHmmss'))
  Copy-Item -LiteralPath $OutputPath -Destination $backup -Force
}

$zipPath = [IO.Path]::ChangeExtension($OutputPath, '.zip')
if (Test-Path -LiteralPath $zipPath) { Remove-Item -LiteralPath $zipPath -Force }
if (Test-Path -LiteralPath $OutputPath) { Remove-Item -LiteralPath $OutputPath -Force }
Compress-Archive -Path (Join-Path $tempRoot '*') -DestinationPath $zipPath -Force
Move-Item -LiteralPath $zipPath -Destination $OutputPath -Force
Remove-Item -LiteralPath $tempRoot -Recurse -Force

Write-Output "CREATED`t$OutputPath"
Write-Output ("COMPONENTS`t" + $componentsRows.Count)
Write-Output ("PORTS`t" + $portsRows.Count)
Write-Output ("ARGUMENTS`t" + $argumentsRows.Count)
Write-Output ("VALUEMAP`t" + $valueMapRows.Count)
Write-Output ("RUNNABLES`t" + $runnablesRows.Count)
