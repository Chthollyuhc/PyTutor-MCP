param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Modules)
# Chạy mỗi module unittest trong DB tạm riêng (không đụng pytutor.db). Dùng: .\.claude\run_isolated.ps1 test_a test_b
$env:PYTHONIOENCODING = "utf-8"; $env:PYTUTOR_DISABLE_LLM = "1"
foreach ($m in $Modules) {
  $tmpDb = Join-Path $env:TEMP ("pytutor_check_" + [guid]::NewGuid().ToString("N") + ".db")
  $tmpKb = Join-Path $env:TEMP ("pytutor_kb_" + [guid]::NewGuid().ToString("N") + ".sqlite3")
  $env:PYTUTOR_DB_PATH = $tmpDb; $env:PYTUTOR_KNOWLEDGE_DB_PATH = $tmpKb
  Write-Host "=== $m ==="
  try { py -m unittest $m 2>&1 | Select-Object -Last 6 }
  finally {
    Remove-Item Env:PYTUTOR_DB_PATH, Env:PYTUTOR_KNOWLEDGE_DB_PATH -ErrorAction SilentlyContinue
    Remove-Item $tmpDb, "$tmpDb-wal", "$tmpDb-shm", $tmpKb -Force -ErrorAction SilentlyContinue
  }
}
