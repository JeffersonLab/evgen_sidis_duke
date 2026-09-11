#!/bin/bash
# Run fitcollins.py and fitsivers.py on any machine that carries the same
# environment as the one this repo was developed on.
#
#   ./run_fits.sh [-n NREP] [-s SEED0] [-w NWORKERS] [-t TMDCUT] [-c COUNTS] [-S SBSDIR] [-d] <rundir> [opt ...]
#
# <rundir>  the run directory, e.g. data_phifull. Must already contain
#           simenhanced3he.dat -- run ./analysis_neutron 3 <rundir> and
#           ./prepare.py <rundir> first.
# [opt ...] which fits to run; default: enhanced3he enhanced3hesyst -- the two
#           SoLID sets for this rundir. 'world' is not in the default: it fits
#           the world data alone, a property of data_world/ rather than of any
#           run, so it gives the same answer whichever directory you pass and
#           belongs with its input -- ./run_fits.sh data_world world, which
#           writes out-world_*.dat into data_world/. ./fitcollins.py with no
#           arguments lists every opt.
#
#   -n NREP       replicas per fit (fit-script default 500)
#   -s SEED0      first seed; disjoint SEED0 give independent ensembles
#   -w NWORKERS   force the worker count, overriding the rule below
#   -t TMDCUT     keep only simulated rows with collinearity R1 < TMDCUT, the
#                 current-fragmentation criterion of arXiv:1611.10329
#                 (tmd.CalculateRfactor). arXiv:2201.12197 uses 0.3, the 2017
#                 paper ~0.2. Off by default. THE WORLD DATA IS NEVER CUT, in
#                 this or any other mode -- the filter sits inside fitsim() and
#                 fitworld() does not call it. Output lands in a suffixed file,
#                 out-<opt>_<obs>_r1lt<TMDCUT>.dat, so an uncut result is never
#                 overwritten. Passing -t with the `world` opt is an error.
#   -c COUNTS     fit the SoLID pseudodata as if the run had COUNTS times the
#                 counts. Every statistical estimator is sqrt(.../Nacc), so this
#                 is exactly stat/sqrt(COUNTS). THE SYSTEMATICS DO NOT MOVE: for
#                 the *syst opts the total error is rebuilt as
#                 sqrt(stat^2/COUNTS + systabs^2 + AUT^2 systrel^2), so the
#                 result says what more beam time actually buys. The world data
#                 and the SBS projection are never scaled. Output lands in
#                 out-<opt>_<obs>[_r1lt<T>]_x<COUNTS>counts.dat, so a nominal
#                 result is never overwritten. Only the SoLID opts accept it.
#   -S SBSDIR     read the SBS projection from SBSDIR instead of data_sbs/. The
#                 SBS set is resolved by the fit scripts through their own SBSDIR,
#                 not through <rundir>, so an alternative SBS binning can only be
#                 fitted this way. data_sbs/split_q2.py makes one.
#   -d            print what would run, run nothing
#   -h            this help
#
# DRYRUN is also readable from the environment. NREP, SEED0 and NWORKERS are not
# read from the environment by the fit scripts at all -- they refuse to run with
# those set, so an old `NREP=10 ./fitcollins.py ...` cannot silently become a
# 500-replica run. This script passes its own values through as flags.
#
# ./run_fits.sh data_phifull                    # the two SoLID fits, 500 replicas
# ./run_fits.sh -n 50 -d data_phifull           # what a 50-replica run would do
# ./run_fits.sh data_world world                # the world fit; it reads and
#                                               # writes data_world/, no rundir
# ./run_fits.sh -t 0.3 data_phifull             # the two SoLID fits, TMD-cut
# ./run_fits.sh -c 4 data_phifull               # the same run with 4x the counts
#
# WORKER COUNT. Half the available CPUs on an ifarm host, all of them
# elsewhere. ifarm nodes are shared interactive machines where taking every
# core makes you the reason someone else's job crawls; a desktop or a batch
# allocation is yours. "Available" means CPUs this process is actually allowed
# to use (sched_getaffinity via nproc), not the machine's core count, so a
# batch allocation of 8 cores on a 128-core node gives 8 (or 4 on ifarm), not
# 128. Override with NWORKERS to ignore all of that.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO"

# Print the leading comment block, however long it grows: from line 2 up to the
# first line that is not a comment. A hardcoded end line silently truncates the
# help the next time the header is edited.
usage() { sed -n '2,$p' "$0" | sed -n '/^[^#]/q;p' | sed 's/^# \{0,1\}//'; }

# Flags before the positionals; each overrides the matching environment variable.
# A non-numeric NREP would otherwise reach python as int('5o0') and die there,
# after the environment is set up and the preflight has passed.
num() { case "$2" in ''|*[!0-9]*) echo "error: $1 must be a positive integer, got '$2'" >&2; exit 2;; esac
        [ "$2" -ge 1 ] || { echo "error: $1 must be >= 1, got '$2'" >&2; exit 2; }; }
# TMDCUT is a threshold on a ratio, so it is a float -- num() above would reject
# 0.3. Validate here rather than let it reach python after the environment setup
# and the preflight have already run.
pos() { case "$2" in ''|*[!0-9.]*|*.*.*|.) echo "error: $1 must be a positive number, got '$2'" >&2; exit 2;; esac
        awk -v v="$2" 'BEGIN{exit !(v+0>0)}' || { echo "error: $1 must be > 0, got '$2'" >&2; exit 2; }; }
while getopts ':n:s:w:t:c:S:dh' flag; do
    case "$flag" in
        n) num NREP "$OPTARG";     NREP="$OPTARG" ;;
        s) case "$OPTARG" in ''|*[!0-9]*) echo "error: SEED0 must be >= 0" >&2; exit 2;; esac
           SEED0="$OPTARG" ;;
        w) num NWORKERS "$OPTARG"; NWORKERS="$OPTARG"; NWSRC="-w flag" ;;
        t) pos TMDCUT "$OPTARG";   TMDCUT="$OPTARG" ;;
        c) pos COUNTS "$OPTARG";   COUNTS="$OPTARG" ;;
        S) [ -d "$OPTARG" ] || { echo "error: -S '$OPTARG' is not a directory" >&2; exit 2; }
           SBSDIR="$OPTARG" ;;
        d) DRYRUN=1 ;;
        h) usage; exit 0 ;;
        :) echo "error: -$OPTARG needs a value" >&2; exit 2 ;;
        ?) echo "error: unknown flag -$OPTARG" >&2; usage >&2; exit 2 ;;
    esac
done
shift $(( OPTIND - 1 ))

if [ $# -lt 1 ]; then
    usage
    exit 0
fi
RUNDIR="$1"; shift
OPTS=("$@")
[ ${#OPTS[@]} -eq 0 ] && OPTS=(enhanced3he enhanced3hesyst)

# The world data is never cut, by any route. fitcollins.py refuses -t with the
# world opt; catch it here too, before the module load and preflight, so a
# mistake costs a second rather than a minute.
if [ -n "${TMDCUT:-}" ]; then
    for o in "${OPTS[@]}"; do
        if [ "$o" = world ]; then
            echo "error: -t does not apply to the 'world' opt -- the world data is never cut." >&2
            echo "       Drop -t, or drop 'world' from the opt list." >&2
            exit 2
        fi
    done
fi

# --counts scales the SoLID pseudodata only. fitcollins.py refuses it for any
# other opt; catch it here too, before the module load, for the same reason -t is
# caught here. Keep this list in step with _COUNTS_OPTS in the fit scripts.
if [ -n "${COUNTS:-}" ]; then
    for o in "${OPTS[@]}"; do
        case "$o" in
            enhanced3he|enhanced3hesyst|sbs+enhanced3he) ;;
            *) echo "error: -c applies only to the SoLID pseudodata opts" >&2
               echo "       (enhanced3he, enhanced3hesyst, sbs+enhanced3he), not '$o'." >&2
               exit 2 ;;
        esac
    done
fi

# ---------------------------------------------------------------- environment
# setup.sh is the bash/zsh port of setup.csh: ROOT via `module`, then the LHAPDF
# paths and the PYTHONPATH for its python bindings.
if [ -r /usr/share/Modules/init/bash ]; then
    # shellcheck disable=SC1091
    source /usr/share/Modules/init/bash
else
    echo "warning: no module init at /usr/share/Modules/init/bash;" >&2
    echo "         assuming ROOT and LHAPDF are already on PATH" >&2
fi
# shellcheck disable=SC1091
source "$REPO/setup.sh"

# ---------------------------------------------------------------- worker count
AVAIL="$(nproc)"
HOST="$(hostname)"
if [ -n "${NWORKERS:-}" ]; then
    WHY="set by ${NWSRC:-the NWORKERS environment variable}"
elif [[ "$HOST" == *ifarm* ]]; then
    NWORKERS=$(( AVAIL / 2 ))
    WHY="host '$HOST' looks like ifarm: half of $AVAIL available CPUs"
else
    NWORKERS="$AVAIL"
    WHY="host '$HOST' is not ifarm: all $AVAIL available CPUs"
fi
[ "$NWORKERS" -lt 1 ] && NWORKERS=1

# One BLAS/OpenMP thread per worker. Without this each of the NWORKERS processes
# may start its own thread pool, and NWORKERS x cores threads on a shared node is
# worse than useless -- it is slower than running serially.
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1

# ---------------------------------------------------------------- preflight
# Each of these has cost a run somewhere. Check them in one second rather than
# discovering the missing one half an hour into a 500-replica fit.
fail=0
say() { printf '  %-34s %s\n' "$1" "$2"; }
command -v root-config >/dev/null 2>&1 && say "ROOT" "$(root-config --version)" \
    || { say "ROOT" "MISSING (module load failed?)"; fail=1; }
command -v lhapdf-config >/dev/null 2>&1 && say "LHAPDF" "$(lhapdf-config --version)" \
    || { say "LHAPDF" "MISSING"; fail=1; }
python3 - <<'PY' || fail=1
import importlib, sys
ok = True
for mod in ('numpy','scipy','pandas','lhapdf'):
    try:
        importlib.import_module(mod)
        print(f"  {mod:<34} ok")
    except Exception as e:
        print(f"  {mod:<34} MISSING ({e.__class__.__name__})"); ok = False
try:
    from iminuit import Minuit
    v = getattr(__import__('iminuit'), '__version__', '?')
    if hasattr(Minuit, 'from_array_func'):
        print(f"  {'iminuit':<34} {v} (has from_array_func)")
    else:
        print(f"  {'iminuit':<34} {v} -- TOO NEW: the fit scripts need iminuit<2"); ok = False
except Exception as e:
    print(f"  {'iminuit':<34} MISSING ({e.__class__.__name__})"); ok = False
try:
    import lhapdf
    for s in ('CJ15lo','DSSFFlo','NNPDFpol11_100'):
        lhapdf.mkPDF(s, 0 if s != 'DSSFFlo' else 211)
        print(f"  {'PDF set '+s:<34} ok")
except Exception as e:
    print(f"  {'PDF sets':<34} MISSING ({e})"); ok = False
sys.exit(0 if ok else 1)
PY
# Which opts read this rundir's prepared SoLID file. 'world' and 'sbs' read
# data_world/ instead, so pointing either at a directory holding no pseudodata is
# legitimate -- ./run_fits.sh data_world world. Everything else here does need it,
# and the check below is why a missing or unprepared file costs a second rather
# than being discovered inside a 500-replica fit.
#
# KEEP THIS LIST IN STEP WITH THE OPT DISPATCH in fitcollins.py/fitsivers.py. An
# opt that reads simenhanced3he.dat but is missing here silently reports
# "not needed (world-only run)" and skips its own preflight -- which is exactly
# what sbs+enhanced3he did when it was added.
NEEDSIM=0
for o in "${OPTS[@]}"; do
    case "$o" in enhanced3he|enhanced3hesyst|sbs+enhanced3he) NEEDSIM=1 ;; esac
done
if [ "$NEEDSIM" -eq 1 ]; then
    [ -f "$RUNDIR/simenhanced3he.dat" ] && say "$RUNDIR/simenhanced3he.dat" "$(wc -l < "$RUNDIR/simenhanced3he.dat") lines" \
        || { say "$RUNDIR/simenhanced3he.dat" "MISSING -- run ./prepare.py $RUNDIR"; fail=1; }
else
    say "$RUNDIR/simenhanced3he.dat" "not needed (world-only run)"
fi
[ -f data_world/colworld_collins.dat ] && [ -f data_world/colworld_sivers.dat ] \
    && say "data_world/colworld_*.dat" "present" \
    || { say "data_world/colworld_*.dat" "MISSING"; fail=1; }

echo
echo "  rundir     $RUNDIR"
echo "  opts       ${OPTS[*]}"
echo "  workers    $NWORKERS   ($WHY)"
echo "  NREP       ${NREP:-500 (script default)}   SEED0 ${SEED0:-0}"
if [ -n "${TMDCUT:-}" ]; then
    echo "  TMD cut    R1 < $TMDCUT   (simulated data only; world never cut)"
else
    echo "  TMD cut    none"
fi
if [ -n "${SBSDIR:-}" ]; then
    echo "  sbsdir     $SBSDIR   (overriding the fit scripts' default)"
fi
if [ -n "${COUNTS:-}" ]; then
    echo "  counts     x$COUNTS   (SoLID stat error /sqrt($COUNTS); systematics unchanged)"
else
    echo "  counts     x1 (as generated)"
fi
echo

if [ "$fail" -ne 0 ]; then
    echo "preflight failed; nothing run." >&2
    exit 1
fi
if [ -n "${DRYRUN:-}" ]; then
    echo "DRYRUN set; nothing run."
    exit 0
fi

# ---------------------------------------------------------------- run
LOG="$RUNDIR/fitlog-$(date +%Y%m%d-%H%M%S).txt"
{
    echo "host $HOST   workers $NWORKERS   NREP ${NREP:-500}   SEED0 ${SEED0:-0}   TMDCUT ${TMDCUT:-none}   COUNTS ${COUNTS:-1}"
    echo "started $(date)"
} | tee "$LOG"

# Pass the knobs as flags now that the fit scripts take them, rather than relying
# on the exported environment. Only pass what was actually asked for, so an
# unset NREP still means "the fit script's own default".
KNOBS=(-w "$NWORKERS")
[ -n "${NREP:-}" ]  && KNOBS+=(-n "$NREP")
[ -n "${SEED0:-}" ] && KNOBS+=(-s "$SEED0")
[ -n "${TMDCUT:-}" ] && KNOBS+=(-t "$TMDCUT")
[ -n "${COUNTS:-}" ] && KNOBS+=(-c "$COUNTS")
[ -n "${SBSDIR:-}" ] && KNOBS+=(-S "$SBSDIR")
# unexport, so the fit scripts' environment check does not fire on our own values
export -n NREP SEED0 NWORKERS 2>/dev/null || true

# One fit at a time, start to finish, in the order printed above. Each fit
# already spreads its replicas over NWORKERS processes, so running two of them
# concurrently would ask for 2 x NWORKERS cores and make both slower -- on a
# shared node, everyone else's too.
rc=0
for script in ./fitcollins.py ./fitsivers.py; do
    for opt in "${OPTS[@]}"; do
        printf '%-16s %-18s ' "$script" "$opt" | tee -a "$LOG"
        t0=$SECONDS
        if "$script" "$opt" "$RUNDIR" "${KNOBS[@]}" >>"$LOG" 2>&1; then
            printf 'OK   %4ds\n' "$(( SECONDS - t0 ))" | tee -a "$LOG"
        else
            printf 'FAILED %2ds  (see %s)\n' "$(( SECONDS - t0 ))" "$LOG" | tee -a "$LOG"
            rc=1
        fi
    done
done

echo "finished $(date)" | tee -a "$LOG"
echo "outputs:"
ls -la "$RUNDIR"/out-*.dat 2>/dev/null | awk '{print "  ", $NF, $5, "bytes"}'
exit "$rc"
