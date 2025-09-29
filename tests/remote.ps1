# TEST LIVE DEPLOYMENT
Write-Host "Testing Live Deployment" -ForegroundColor Green
Write-Host "URL: https://trading-production-6fd9.up.railway.app/" -ForegroundColor Cyan

$BaseUrl = "https://trading-production-6fd9.up.railway.app"

# Use volatile stocks
$volatileStocks = @("TSLA", "MSTR", "COIN", "NVDA", "AMD")

foreach ($stock in $volatileStocks) {
    Write-Host "Testing: $stock" -ForegroundColor Cyan
    
    # Reset and set up
    Invoke-RestMethod -Uri "$BaseUrl/emergency-exit" -Method Post | Out-Null
    Start-Sleep -Seconds 1
    
    $body = @{ticker = $stock} | ConvertTo-Json
    Invoke-RestMethod -Uri "$BaseUrl/start" -Method Post -Body $body -ContentType "application/json"
    
    $body = @{profile = "risky_business"} | ConvertTo-Json
    Invoke-RestMethod -Uri "$BaseUrl/set-profile" -Method Post -Body $body -ContentType "application/json"
    
    $body = @{strategy = "scalping"} | ConvertTo-Json
    Invoke-RestMethod -Uri "$BaseUrl/set-strategy" -Method Post -Body $body -ContentType "application/json"
    
    # Monitor for 30 seconds
    for ($i = 1; $i -le 6; $i++) {
        $state = Invoke-RestMethod -Uri "$BaseUrl/state" -Method Get
        if ($state.current_state -eq "LONG") {
            Write-Host "SUCCESS! $stock TRADE EXECUTED!" -ForegroundColor Green
            Write-Host "Bought $($state.position.quantity) shares at $$($state.position.entry_price)" -ForegroundColor Green
            break
        }
        Write-Host "Check $i : No trade yet" -ForegroundColor Gray
        Start-Sleep -Seconds 5
    }
    
    if ($state.current_state -eq "LONG") {
        break
    }
}

if ($state.current_state -ne "LONG") {
    Write-Host "No trades executed with any stock." -ForegroundColor Red
    Write-Host "The trading conditions may be too strict." -ForegroundColor Yellow
}