param(
  [string]$RepoRoot = (Resolve-Path ".").Path
)

$src = Join-Path $RepoRoot "csv"
$dst = Join-Path $RepoRoot "data/raw"

if (-not (Test-Path $src)) {
  throw "No existe la carpeta origen: $src"
}

New-Item -ItemType Directory -Force -Path $dst | Out-Null

$files = @(
  "Dim_Proyecto.csv",
  "Dim_TipoEnergia.csv",
  "Dim_Regulacion.csv",
  "Fact_Generacion_1000.csv",
  "Fact_Costos.csv",
  "Fact_Cobertura.csv",
  "Fact_ImpactoAmbiental.csv"
)

foreach ($f in $files) {
  $from = Join-Path $src $f
  $to = Join-Path $dst $f
  if (-not (Test-Path $from)) {
    Write-Warning "Falta: $from"
    continue
  }
  Copy-Item -Force $from $to
  Write-Host "Copiado: $f -> data/raw/"
}

Write-Host "Listo. La app preferirá data/raw/, con fallback a csv/."

