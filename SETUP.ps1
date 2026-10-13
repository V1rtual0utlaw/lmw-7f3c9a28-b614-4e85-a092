param([switch]$InstallOnly)
$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$Root = $PSScriptRoot
Set-Location -LiteralPath $Root
New-Item -ItemType Directory -Force -Path "$Root\runtime", "$Root\models", "$Root\logs" | Out-Null

function Refresh-Path {
    $env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')
}
function Native([string]$Exe, [string[]]$Arguments) {
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Exe failed (exit $LASTEXITCODE). See logs\bootstrap.log." }
}
function Install-Package([string]$Id) {
    Write-Host "Installing $Id ..." -ForegroundColor Cyan
    & winget install --exact --id $Id --source winget --accept-source-agreements --accept-package-agreements --disable-interactivity
    if ($LASTEXITCODE -notin @(0,-1978335189)) { throw "Installation of $Id failed. Windows may require an installation prompt or a restart. Re-run SETUP_AND_START.bat after resolving it." }
    Refresh-Path
}
function Download([string]$Url, [string]$Path, [long]$Minimum, [string]$Digest='') {
    if ((Test-Path -LiteralPath $Path) -and (Get-Item -LiteralPath $Path).Length -ge $Minimum) {
        if (!$Digest -or (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLower() -eq $Digest.ToLower()) { return }
    }
    Write-Host "Downloading $(Split-Path $Path -Leaf) ..." -ForegroundColor Cyan
    $Temp = "$Path.partial"
    # Only complete downloads are promoted. A failed setup is safe to run again.
    Native 'curl.exe' @('--fail','--location','--retry','4','--output',$Temp,$Url)
    if ((Get-Item -LiteralPath $Temp).Length -lt $Minimum) { throw "Download is unexpectedly small: $Url" }
    if ($Digest -and (Get-FileHash -LiteralPath $Temp -Algorithm SHA256).Hash.ToLower() -ne $Digest.ToLower()) { throw "Download checksum mismatch: $Url" }
    Move-Item -LiteralPath $Temp -Destination $Path -Force
}
try {
    if (![Environment]::Is64BitOperatingSystem) { throw '64-bit Windows is required.' }
    if (!(Get-Command winget -ErrorAction SilentlyContinue)) { throw 'Windows App Installer (winget) is missing. Install App Installer from Microsoft Store, then re-run this setup.' }
    Write-Host 'True Science Stories automatic local setup' -ForegroundColor Green
    Write-Host 'Downloads free local tools and models. Allow at least 40 GB free space; first run can take a long time.'
    Write-Host 'Installs Python, FFmpeg, Ollama and 7-Zip through winget if needed. Software/model licenses apply.'
    $Drive = Get-PSDrive -Name ([IO.Path]::GetPathRoot($Root).TrimEnd('\').TrimEnd(':')) -ErrorAction SilentlyContinue
    if ($Drive -and $Drive.Free -lt 40GB) { throw 'Please extract the factory onto a drive with at least 40 GB free space.' }
    $Py = "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe"
    if (!(Test-Path -LiteralPath $Py)) {
        $Candidates = @("$env:ProgramFiles\Python311\python.exe")
        $Found = $Candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
        if ($Found) { $Py=$Found } else {
            Install-Package 'Python.Python.3.11'
            if (!(Test-Path -LiteralPath $Py)) {
                if (Get-Command py -ErrorAction SilentlyContinue) { $Py = (& py -3.11 -c 'import sys; print(sys.executable)').Trim() }
                else { throw 'Python installed but not found. Close this window and run setup again.' }
            }
        }
    }
    if (!(Get-Command ffmpeg -ErrorAction SilentlyContinue)) { Install-Package 'Gyan.FFmpeg' }
    if (!(Get-Command ffprobe -ErrorAction SilentlyContinue)) { throw 'FFprobe not found after installation. Re-run setup in a new window.' }
    if (!(Get-Command ollama -ErrorAction SilentlyContinue)) { Install-Package 'Ollama.Ollama' }
    $Seven = "$env:ProgramFiles\7-Zip\7z.exe"
    if (!(Test-Path -LiteralPath $Seven)) {
        if (Get-Command 7z -ErrorAction SilentlyContinue) { $Seven=(Get-Command 7z).Source }
        else { Install-Package '7zip.7zip' }
    }
    if (!(Test-Path -LiteralPath $Seven)) { throw '7-Zip not found. Re-run setup after installation completes.' }
    $Venv = "$Root\runtime\venv\Scripts\python.exe"
    if (!(Test-Path -LiteralPath $Venv)) { Native $Py @('-m','venv',"$Root\runtime\venv") }
    Native $Venv @('-m','pip','install','piper-tts')
    $Voice = 'en_US-ljspeech-high'
    if (!(Test-Path "$Root\models\$Voice.onnx") -or !(Test-Path "$Root\models\$Voice.onnx.json")) {
        Push-Location "$Root\models"
        try { Native $Venv @('-m','piper.download_voices',$Voice) } finally { Pop-Location }
    }
    $Comfy = "$Root\runtime\ComfyUI_windows_portable"
    if (!(Test-Path "$Comfy\python_embeded\python.exe")) {
        $Release = Invoke-RestMethod 'https://api.github.com/repos/Comfy-Org/ComfyUI/releases/latest' -Headers @{'User-Agent'='TrueScienceStories-Setup'}
        # Prefer CUDA 12.6 when offered for broader NVIDIA driver compatibility.
        $Asset = $Release.assets | Where-Object { $_.name -match 'windows_portable_nvidia.*cu126.*\.7z$' } | Select-Object -First 1
        if (!$Asset) { $Asset = $Release.assets | Where-Object { $_.name -eq 'ComfyUI_windows_portable_nvidia.7z' } | Select-Object -First 1 }
        if (!$Asset) { throw 'Official ComfyUI portable NVIDIA package not found. No substitute download was used.' }
        $Digest=''
        if ($Asset.digest -like 'sha256:*') { $Digest=$Asset.digest.Substring(7) }
        $Archive="$Root\runtime\comfy.7z"
        Download $Asset.browser_download_url $Archive 100000000 $Digest
        Native $Seven @('x',$Archive,"-o$Root\runtime",'-y')
        if (!(Test-Path "$Comfy\python_embeded\python.exe")) { throw 'ComfyUI archive layout changed. See setup.log.' }
    }
    $Checkpoint='v1-5-pruned-emaonly.safetensors'
    $Model="$Comfy\ComfyUI\models\checkpoints\$Checkpoint"
    # Hugging Face's LFS metadata supplies the model's SHA-256 when available.
    $Meta=Invoke-RestMethod 'https://huggingface.co/api/models/stable-diffusion-v1-5/stable-diffusion-v1-5?blobs=true'
    $Entry=$Meta.siblings | Where-Object { $_.rfilename -eq $Checkpoint } | Select-Object -First 1
    if (!$Entry.lfs.sha256) { throw 'Unable to obtain checkpoint checksum from its official model repository.' }
    Download "https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/main/$Checkpoint" $Model 1000000000 $Entry.lfs.sha256
    $Workflow=Get-Content -LiteralPath "$Root\workflow.json" -Raw | ConvertFrom-Json
    $Workflow.'4'.inputs.ckpt_name=$Checkpoint
    $Workflow | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath "$Root\workflow.json" -Encoding UTF8
    $Config=Get-Content -LiteralPath "$Root\config.json" -Raw | ConvertFrom-Json
    $Config | Add-Member -NotePropertyName piper_python -NotePropertyValue $Venv -Force
    $Config.voice="models/$Voice.onnx"
    $Config | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath "$Root\config.json" -Encoding UTF8
    @{python=$Venv;comfy=$Comfy;ollama=(Get-Command ollama).Source;ffmpeg=(Get-Command ffmpeg).Source} | ConvertTo-Json | Set-Content -LiteralPath "$Root\runtime\installed.json" -Encoding UTF8
    # Start local endpoints and check dependencies before opening the UI.
    Native $Venv @("$Root\launch.py",'--prepare')
    Native (Get-Command ollama).Source @('pull',$Config.model)
    Native $Venv @('-m','piper','-m',"$Root\models\$Voice.onnx",'-f',"$Root\runtime\voice-test.wav",'--','The local factory is ready.')
    Native $Venv @("$Root\doctor.py")
    Write-Host 'Setup complete. START_WINDOWS.bat starts the factory next time.' -ForegroundColor Green
    if (!$InstallOnly) { Native $Venv @("$Root\launch.py") }
} catch {
    Write-Host "SETUP STOPPED: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host 'Details: logs\bootstrap.log. Fix the reported issue and run the same launcher again.'
    exit 1
}
