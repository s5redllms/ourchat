# OurChat Production Readiness Test Runner
# PowerShell script to run comprehensive production tests

param(
    [string]$Url = "http://localhost:5000",
    [switch]$Verbose = $false,
    [switch]$Quick = $false,
    [switch]$InstallDeps = $false,
    [switch]$StartServer = $false
)

Write-Host "🚀 OurChat Production Readiness Test Runner" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.7+ first." -ForegroundColor Red
    exit 1
}

# Install dependencies if requested
if ($InstallDeps) {
    Write-Host "📦 Installing test dependencies..." -ForegroundColor Yellow
    
    if (Test-Path "test_requirements.txt") {
        pip install -r test_requirements.txt
    } else {
        # Install basic requirements manually
        pip install requests psutil Pillow Flask Flask-SQLAlchemy Werkzeug
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}

# Start server if requested
$serverProcess = $null
if ($StartServer) {
    Write-Host "🌐 Starting OurChat server..." -ForegroundColor Yellow
    
    # Check if app.py exists
    if (Test-Path "app.py") {
        $serverProcess = Start-Process python -ArgumentList "app.py" -PassThru -WindowStyle Minimized
        Write-Host "✅ Server started (PID: $($serverProcess.Id))" -ForegroundColor Green
        Write-Host "⏳ Waiting 5 seconds for server to initialize..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    } else {
        Write-Host "❌ app.py not found. Cannot start server." -ForegroundColor Red
        exit 1
    }
}

# Prepare test arguments
$testArgs = @()
$testArgs += "--url", $Url

if ($Verbose) {
    $testArgs += "--verbose"
}

if ($Quick) {
    $testArgs += "--quick"
}

Write-Host "🧪 Running production readiness tests..." -ForegroundColor Yellow
Write-Host "   Target URL: $Url" -ForegroundColor Gray
Write-Host "   Verbose: $Verbose" -ForegroundColor Gray
Write-Host "   Quick mode: $Quick" -ForegroundColor Gray
Write-Host ""

try {
    # Run the test script
    python production_readiness_test.py @testArgs
    $testExitCode = $LASTEXITCODE
    
    Write-Host ""
    Write-Host "📊 Test Results:" -ForegroundColor Cyan
    
    # Check for generated reports
    $reportFiles = Get-ChildItem -Filter "production_readiness_report_*.html" | Sort-Object LastWriteTime -Descending
    if ($reportFiles.Count -gt 0) {
        $latestReport = $reportFiles[0]
        Write-Host "📄 HTML Report: $($latestReport.FullName)" -ForegroundColor Green
        
        # Ask if user wants to open the report
        $openReport = Read-Host "Would you like to open the HTML report? (y/n)"
        if ($openReport -eq 'y' -or $openReport -eq 'Y') {
            Start-Process $latestReport.FullName
        }
    }
    
    # Display final result
    if ($testExitCode -eq 0) {
        Write-Host "🎉 Tests completed successfully! Application appears production-ready." -ForegroundColor Green
    } else {
        Write-Host "⚠️  Tests identified issues that need attention before production." -ForegroundColor Red
    }
    
} catch {
    Write-Host "💥 Error running tests: $_" -ForegroundColor Red
    $testExitCode = 1
} finally {
    # Clean up server process if we started it
    if ($serverProcess -and !$serverProcess.HasExited) {
        Write-Host "🛑 Stopping test server..." -ForegroundColor Yellow
        Stop-Process -Id $serverProcess.Id -Force
        Write-Host "✅ Server stopped" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Test run completed. Exit code: $testExitCode" -ForegroundColor Cyan

# Set exit code for CI/CD integration
exit $testExitCode
