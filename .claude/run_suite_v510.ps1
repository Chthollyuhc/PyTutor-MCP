param([string]$OutDir = "evaluation\v510_baseline", [switch]$SkipFrontend)
# Chạy toàn bộ bộ hồi quy v5.10: mỗi module một DB tạm riêng, LLM tắt, lưu đầu ra thô vào $OutDir.
# Dùng: .\.claude\run_suite_v510.ps1 -OutDir evaluation\v510_baseline
$ErrorActionPreference = "Continue"
$env:PYTHONIOENCODING = "utf-8"; $env:PYTUTOR_DISABLE_LLM = "1"
New-Item -ItemType Directory -Force $OutDir | Out-Null
$summary = New-Object System.Collections.ArrayList

function Invoke-Isolated([string]$Name, [scriptblock]$Cmd) {
  $tmpDb = Join-Path $env:TEMP ("pytutor_check_" + [guid]::NewGuid().ToString("N") + ".db")
  $tmpKb = Join-Path $env:TEMP ("pytutor_kb_" + [guid]::NewGuid().ToString("N") + ".sqlite3")
  $env:PYTUTOR_DB_PATH = $tmpDb; $env:PYTUTOR_KNOWLEDGE_DB_PATH = $tmpKb
  $log = Join-Path $OutDir ($Name + ".txt")
  $t0 = Get-Date
  try { & $Cmd 2>&1 | Out-File -FilePath $log -Encoding utf8 }
  finally {
    Remove-Item Env:PYTUTOR_DB_PATH, Env:PYTUTOR_KNOWLEDGE_DB_PATH -ErrorAction SilentlyContinue
    Remove-Item $tmpDb, "$tmpDb-wal", "$tmpDb-shm", $tmpKb -Force -ErrorAction SilentlyContinue
  }
  $tail = (Get-Content $log -Tail 4) -join " | "
  $secs = [int]((Get-Date) - $t0).TotalSeconds
  [void]$summary.Add(("{0} ({1}s): {2}" -f $Name, $secs, $tail))
  Write-Host ("{0} ({1}s): {2}" -f $Name, $secs, $tail)
}

py -m compileall -q backend mcp_server pytutor_shared 2>&1 | Out-File (Join-Path $OutDir "compileall.txt") -Encoding utf8
[void]$summary.Add("compileall exit=$LASTEXITCODE")

$unit = "test_phase16_ai_upgrade test_phase17_adaptive_analytics test_qa_authorization test_thesis_upgrade test_level3_scaffold test_pedagogy_v55 test_learner_model test_passwords test_no_code_hint test_user_uploaded_kb test_data_capture_v57 test_class_overview_v57 test_visual_views_v58 test_plain_language_v59 test_phase5_backend test_phase8_chat test_phase9_visualizer test_phase10_gamification test_phase12_classroom_exam test_phase13_14_neu_lms test_phase15_3_qa_audit test_phase15_4_action_buttons".Split(" ")
# Các module bổ sung (v5.10) nếu có
foreach ($extra in @("test_hint_quality_v510", "test_hint_evidence_v510", "test_prompt_golden_v510", "test_hint_resilience_v510")) { if (Test-Path "$extra.py") { $unit += $extra } }
$scripts = "test_phase5_backend test_phase8_chat test_phase9_visualizer test_phase10_gamification test_phase12_classroom_exam test_phase13_14_neu_lms test_phase15_3_qa_audit test_phase15_4_action_buttons".Split(" ")
foreach ($m in $unit) {
  if ($scripts -contains $m) { Invoke-Isolated $m { py "$m.py" } }  # kịch bản: chạy trực tiếp, không phải unittest
  else { Invoke-Isolated $m { py -m unittest $m -v } }
}
Invoke-Isolated "mcp_test_mcp_server" { py -m mcp_server.test_mcp_server }
Invoke-Isolated "backend_test_backend_e2e" { py -m backend.test_backend_e2e }
Invoke-Isolated "eval_phase17_adaptive" { py evaluate_phase17_adaptive.py }
Invoke-Isolated "eval_learner_model_policy" { py evaluate_learner_model_policy.py }
Invoke-Isolated "eval_guardrails_dev" { py evaluate_guardrails_benchmark.py }
Invoke-Isolated "eval_guardrails_holdout" { py evaluate_guardrails_benchmark.py --holdout }
Invoke-Isolated "eval_rag" { py evaluate_rag_benchmark.py }
Invoke-Isolated "eval_level3_dev" { py evaluate_level3_skeleton.py }
Invoke-Isolated "eval_level3_holdout" { py evaluate_level3_skeleton.py --holdout }
if (-not $SkipFrontend) {
  Push-Location frontend
  foreach ($s in @("test:theme", "test:ui-utils", "build")) {
    $t0 = Get-Date
    npm.cmd run $s 2>&1 | Out-File (Join-Path ("..\" + $OutDir) ("frontend_" + ($s -replace ":", "_") + ".txt")) -Encoding utf8
    $secs = [int]((Get-Date) - $t0).TotalSeconds
    $tail = (Get-Content (Join-Path ("..\" + $OutDir) ("frontend_" + ($s -replace ":", "_") + ".txt")) -Tail 3) -join " | "
    [void]$summary.Add("frontend $s ($secs s): $tail")
    Write-Host "frontend $s ($secs s): $tail"
  }
  Pop-Location
}
$summary | Out-File (Join-Path $OutDir "SUMMARY.txt") -Encoding utf8
Write-Host "DONE -> $OutDir\SUMMARY.txt"
