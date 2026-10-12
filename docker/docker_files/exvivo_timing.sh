#!/usr/bin/env bash
# Step wall-clock times. Source from launchers; do not invoke commands via eval.
: "${EXVIVO_TIMING_DIR:?EXVIVO_TIMING_DIR must be set}"
timing_utc() { date -u +%Y-%m-%dT%H:%M:%SZ; }
timing_append() {
    local file=$1
    shift
    mkdir -p "$EXVIVO_TIMING_DIR"
    if [[ ! -s "$file" ]]; then
        printf 'stage\tstep\tname\tstart_utc\tend_utc\telapsed_seconds\texit_code\n' > "$file"
    fi
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$@" >> "$file"
}
timed_step() {
    local stage=$1 step=$2 name=$3
    shift 3
    local started ended start_utc rc duration
    started=$(date +%s)
    start_utc=$(timing_utc)
    printf '[%s %s] %s — started %s\n' "$stage" "$step" "$name" "$start_utc"
    # Commands are single external calls or one-command helper functions.
    # Invoked bash scripts enforce their own set -e/pipefail.
    if "$@"; then rc=0; else rc=$?; fi
    ended=$(date +%s)
    duration=$((ended-started))
    timing_append "$EXVIVO_TIMING_DIR/step_timings.tsv" \
        "$stage" "$step" "$name" "$start_utc" "$(timing_utc)" "$duration" "$rc"
    printf '[%s %s] %s — %02d:%02d:%02d, exit %d\n' \
        "$stage" "$step" "$name" "$((duration/3600))" "$((duration/60%60))" "$((duration%60))" "$rc"
    return "$rc"
}
timing_total() {
    local stage=$1 started=$2 start_utc=$3 rc=$4
    local duration=$(( $(date +%s) - started ))
    timing_append "$EXVIVO_TIMING_DIR/run_summary.tsv" \
        "$stage" total "$stage total" "$start_utc" "$(timing_utc)" "$duration" "$rc"
    printf '[%s total] %02d:%02d:%02d, exit %d\n' \
        "$stage" "$((duration/3600))" "$((duration/60%60))" "$((duration%60))" "$rc"
}
