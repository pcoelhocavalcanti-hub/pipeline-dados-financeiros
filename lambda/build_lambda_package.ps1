# Monta o pacote de deploy da Lambda (handler.py + dependencias para Linux x86_64)
# sem precisar de Docker, baixando wheels manylinux diretamente via pip.
# Rode a partir da pasta lambda/. Gera build.zip, usado pelo terraform apply.

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

if (Test-Path "package") { Remove-Item "package" -Recurse -Force }
if (Test-Path "build.zip") { Remove-Item "build.zip" -Force }

python -m pip install `
  --target package `
  --platform manylinux2014_x86_64 `
  --implementation cp `
  --python-version 3.12 `
  --only-binary=:all: `
  -r requirements.txt

Copy-Item "handler.py" "package/handler.py"

Compress-Archive -Path "package\*" -DestinationPath "build.zip" -CompressionLevel Optimal

$size = (Get-Item "build.zip").Length / 1MB
Write-Output "build.zip gerado ($([math]::Round($size,1)) MB)"
