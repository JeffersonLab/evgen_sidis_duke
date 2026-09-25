#!/bin/bash
# Draw phicompare studies with the two notebooks.
#
#   ./run_phicompare.sh [study ...]      default: every gallery/input-*.csv
#
# A study is gallery/input-<study>.csv (format: the notebooks' "Load the study's
# fits" cell, and README.md). For each study both notebooks run with
# PHICOMPARE_STUDY=<study> and write gallery/<figure>-<study>.pdf plus
# gallery/{trans,sivers}-tables-<study>.md. The executed notebooks are thrown away
# for every study except `enhanced3he-main`, which is run last and in place, so the
# notebooks on disk always show it.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
if [ -f /usr/share/Modules/init/bash ]; then . /usr/share/Modules/init/bash; fi
set +u; . ../setup.sh; set -u

if [ $# -eq 0 ]; then
    set -- $(ls gallery/input-*.csv | sed 's#gallery/input-##; s#\.csv$##')
fi
for s in "$@"; do
    [ -f "gallery/input-$s.csv" ] || { echo "no gallery/input-$s.csv" >&2; exit 1; }
done

run() {   # run <study> <notebook>
    if [ "$1" = enhanced3he-main ]; then
        PHICOMPARE_STUDY=enhanced3he-main jupyter nbconvert --to notebook --execute --inplace \
            --ExecutePreprocessor.timeout=3600 "$2"
    else
        PHICOMPARE_STUDY="$1" jupyter nbconvert --to notebook --execute --stdout \
            --ExecutePreprocessor.timeout=3600 "$2" > /dev/null
    fi
}

# enhanced3he-main last, so the in-place notebooks end on it; both observables in parallel
for s in $(printf '%s\n' "$@" | grep -vx enhanced3he-main) $(printf '%s\n' "$@" | grep -x enhanced3he-main); do
    echo "== $s   $(date +%H:%M:%S)"
    run "$s" plot-transversity_phicompare.ipynb & t=$!
    run "$s" plot-sivers_phicompare.ipynb       & v=$!
    wait $t; wait $v
done
echo "== done   $(date +%H:%M:%S)"
