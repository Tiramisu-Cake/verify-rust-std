#!/bin/sh
# usage: run.sh <gen script> <seconds> <a:b> ...      e.g.  ./run.sh gen.py 60 net13:qform_lemma
# SOLVER defaults to the bundled minimal CDCL; set SOLVER=kissat (or cadical) to use a real solver.
D=$(cd "$(dirname "$0")" && pwd); G=$1; LIM=$2; shift 2
for mo in "$@"; do
  a=${mo%%:*}; b=${mo##*:}; f=$D/cnf_$(basename $G .py)_${a}_${b}.cnf
  python3 "$D/$G" $a $b "$f" >/dev/null || { echo "$a $b GENFAIL"; continue; }
  if [ -n "$SOLVER" ]; then /usr/bin/time -f "%es wall" timeout $LIM $SOLVER -q "$f" 2>&1 | tr '\n' ' '; echo " <- $a $b";
  else echo "$a $b $("$D/cdcl" "$f" 50000000 $LIM)"; fi
done
