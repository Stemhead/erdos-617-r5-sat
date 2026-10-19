#!/bin/zsh
# prints one line whenever any attack on the last cube reaches a terminal state; exits when all have reported
cd /private/tmp/claude-501/-Users-glenhowell/1e74946d-d297-4adb-89ee-6edef76e6122/scratchpad/p617
seen=""
while true; do
  l=$(grep -E "\(5, 4, 4, 4, 4\) E=39 .*(UNSAT|SAT)|^DONE|Traceback" k21_low.log | tail -1)
  [ -n "$l" ] && [[ "$seen" != *"[plain]"* ]] && { echo "[plain] $l"; seen="${seen}[plain]"; }
  for f in kissat_54444_39 kissat_55443_39; do
    l=$(grep -E "kissat|Traceback" $f.log | tail -1); [ -n "$l" ] && [[ "$seen" != *"[$f]"* ]] && { echo "[$f] $l"; seen="${seen}[$f]"; }
  done
  for f in low_5-5-4-4-3_E39 low_5-4-4-4-4_E39; do
    l=$(grep "^s " certs21b/$f.out 2>/dev/null); [ -n "$l" ] && [[ "$seen" != *"[c3 $f]"* ]] && { echo "[cadical3 $f] $l proof=$(ls -la certs21b/$f.drat | awk '{printf "%.1fGB",$5/1073741824}')"; seen="${seen}[c3 $f]"; }
  done
  for f in low_5-5-4-4-3_E39 low_5-4-4-4-4_E39; do
    l=$(grep -E "^s |ERROR|WARNING: .*(proof|fail)" certs21b/$f.check 2>/dev/null | tail -1); [ -n "$l" ] && [[ "$seen" != *"[chk $f]"* ]] && { echo "[drat-trim $f] $l"; seen="${seen}[chk $f]"; }
  done
  l=$(grep -E "CHECK-FAILED|: SAT|CERT DONE|Traceback" k21_cert.log | tail -1); [ -n "$l" ] && [[ "$seen" != *"[cert]"* ]] && { echo "[cert] $l"; seen="${seen}[cert]"; }
  l=$(grep "VERIFIED" k21_cert.log | tail -1 | grep "39)"); [ -n "$l" ] && [[ "$seen" != *"[certv]"* ]] && { echo "[cert] $l"; seen="${seen}[certv]"; }
  l=$(grep -E "UNSAT|SAT|Traceback" k21c39.log | tail -1); [ -n "$l" ] && [[ "$seen" != *"[c39:$l]"* ]] && { echo "[k21c39] $l  ($(grep -c UNSAT k21c39.log)/150 done)"; seen="${seen}[c39:$l]"; }
  pgrep -f "build/cadical" >/dev/null || pgrep -f "k21.py 4 emax" >/dev/null || pgrep -f "drat-trim" >/dev/null || { echo "all solver processes gone"; break; }
  sleep 30
done
