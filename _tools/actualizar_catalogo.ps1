param(
    [Parameter(Mandatory = $true)]
    [string]$Csv,
    [string]$Fotos,
    [switch]$PermitirRetirados
)

$ErrorActionPreference = "Stop"
$OutputEncoding = [System.Text.UTF8Encoding]::new()
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$env:PYTHONUTF8 = "1"
$repo = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$csvPath = (Resolve-Path -LiteralPath $Csv).Path

Push-Location $repo
try {
    if ($Fotos) {
        $photoPath = (Resolve-Path -LiteralPath $Fotos).Path
        python _tools/procesar_fotos.py $photoPath --sobrescribir
        if ($LASTEXITCODE -ne 0) { throw "Falló el procesamiento de fotografías." }
    }

    $syncArgs = @("_tools/sincronizar_catalogo.py", $csvPath, "--aplicar")
    if ($PermitirRetirados) { $syncArgs += "--permitir-retirados" }
    python @syncArgs
    if ($LASTEXITCODE -ne 0) { throw "El CSV no pasó la validación del catálogo." }

    python _tools/publicar_v3.py --origin https://bolemsv.com
    if ($LASTEXITCODE -ne 0) { throw "Falló la generación del sitio." }
    python _tools/verificar.py
    if ($LASTEXITCODE -ne 0) { throw "Falló la verificación principal." }
    python v3/_source/verify.py
    if ($LASTEXITCODE -ne 0) { throw "Falló la verificación de páginas." }
    python _tools/verificar_publicacion.py
    if ($LASTEXITCODE -ne 0) { throw "Falló la verificación de publicación." }

    Write-Host "Catálogo generado y verificado. Revise el diff antes de publicar." -ForegroundColor Green
}
finally {
    Pop-Location
}
