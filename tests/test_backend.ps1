# Comprehensive Trading Test
Write-Host "Starting Comprehensive Trading Tests..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow

$BaseUrl = "http://localhost:8000"

# Function to make API calls
function Invoke-TradingAPI {
    param($Method, $Endpoint, $Body)
    
    try {
        if ($Method -eq "POST" -and $Body) {
            $jsonBody = $Body | ConvertTo-Json
            $result = Invoke-RestMethod -Uri "$BaseUrl$Endpoint" -Method Post -Body $jsonBody -ContentType "application/json"
        } else {
            $result = Invoke-RestMethod -Uri "$BaseUrl$Endpoint" -Method $Method
        }
        return @{ Success = $true; Data = $result }
    } catch {
        return @{ Success = $false; Error = $_.Exception.Message }
    }
}

# Test 1: Start Trading Strategy
Write-Host "`n1. Starting Trading Strategy for SPY..." -ForegroundColor Cyan
$startResult = Invoke-TradingAPI -Method "POST" -Endpoint "/start" -Body @{ticker = "SPY"}
if ($startResult.Success) {
    Write-Host "   SUCCESS: $($startResult.Data.message)" -ForegroundColor Green
} else {
    Write-Host "   FAILED: $($startResult.Error)" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# Test 2: Check Active State
Write-Host "`n2. Checking Strategy Status..." -ForegroundColor Cyan
$stateResult = Invoke-TradingAPI -Method "GET" -Endpoint "/state"
if ($stateResult.Success) {
    $state = $stateResult.Data
    Write-Host "   Current State: $($state.current_state)" -ForegroundColor Green
    Write-Host "   Strategy Active: $($state.strategy_active)" -ForegroundColor Green
    Write-Host "   Ticker: $($state.ticker)" -ForegroundColor Green
} else {
    Write-Host "   FAILED: $($stateResult.Error)" -ForegroundColor Red
}

# Test 3: Set Risk Profile
Write-Host "`n3. Setting Risk Profile to 'risky_business'..." -ForegroundColor Cyan
$profileResult = Invoke-TradingAPI -Method "POST" -Endpoint "/set-profile" -Body @{profile = "risky_business"}
if ($profileResult.Success) {
    Write-Host "   SUCCESS: $($profileResult.Data.message)" -ForegroundColor Green
} else {
    Write-Host "   FAILED: $($profileResult.Error)" -ForegroundColor Red
}

# Test 4: Check Available Strategies
Write-Host "`n4. Checking Available Strategies..." -ForegroundColor Cyan
$strategiesResult = Invoke-TradingAPI -Method "GET" -Endpoint "/strategies"
if ($strategiesResult.Success) {
    $strategies = $strategiesResult.Data.strategies -join ", "
    Write-Host "   Available Strategies: $strategies" -ForegroundColor Green
} else {
    Write-Host "   FAILED: $($strategiesResult.Error)" -ForegroundColor Red
}

# Test 5: Set Trading Strategy
Write-Host "`n5. Setting Trading Strategy to 'momentum'..." -ForegroundColor Cyan
$strategyResult = Invoke-TradingAPI -Method "POST" -Endpoint "/set-strategy" -Body @{strategy = "momentum"}
if ($strategyResult.Success) {
    Write-Host "   SUCCESS: $($strategyResult.Data.message)" -ForegroundColor Green
} else {
    Write-Host "   FAILED: $($strategyResult.Error)" -ForegroundColor Red
}

# Test 6: Check Recent Trading Activity
Write-Host "`n6. Checking Recent Trading Activity..." -ForegroundColor Cyan
$logsResult = Invoke-TradingAPI -Method "GET" -Endpoint "/logs?limit=10"
if ($logsResult.Success) {
    Write-Host "   Recent Log Entries:" -ForegroundColor Green
    $logsResult.Data | ForEach-Object {
        $time = if ($_.timestamp) { $_.timestamp.Substring(11,8) } else { "Unknown" }
        $event = $_.event
        $message = $_.message
        Write-Host "   [$time] $event - $message" -ForegroundColor Gray
    }
} else {
    Write-Host "   FAILED: $($logsResult.Error)" -ForegroundColor Red
}

# Test 7: Monitor for 30 seconds to see if any trades execute
Write-Host "`n7. Monitoring for Trading Activity (30 seconds)..." -ForegroundColor Cyan
Write-Host "   Watching for BUY/SELL signals..." -ForegroundColor Yellow

for ($i = 1; $i -le 6; $i++) {
    Start-Sleep -Seconds 5
    $currentState = Invoke-TradingAPI -Method "GET" -Endpoint "/state"
    if ($currentState.Success) {
        $state = $currentState.Data
        Write-Host "   Check $i : State=$($state.current_state), Active=$($state.strategy_active)" -ForegroundColor Gray
    }
}

# Test 8: Pause Strategy
Write-Host "`n8. Pausing Trading Strategy..." -ForegroundColor Cyan
$pauseResult = Invoke-TradingAPI -Method "POST" -Endpoint "/pause"
if ($pauseResult.Success) {
    Write-Host "   SUCCESS: $($pauseResult.Data.message)" -ForegroundColor Green
} else {
    Write-Host "   FAILED: $($pauseResult.Error)" -ForegroundColor Red
}

# Test 9: Final State Check
Write-Host "`n9. Final System State..." -ForegroundColor Cyan
$finalState = Invoke-TradingAPI -Method "GET" -Endpoint "/state"
if ($finalState.Success) {
    $state = $finalState.Data
    Write-Host "   Final State: $($state.current_state)" -ForegroundColor Green
    Write-Host "   Strategy Active: $($state.strategy_active)" -ForegroundColor Green
    Write-Host "   Equity: `$$($state.equity)" -ForegroundColor Green
} else {
    Write-Host "   FAILED: $($finalState.Error)" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Yellow
Write-Host "Trading Tests Completed!" -ForegroundColor Yellow