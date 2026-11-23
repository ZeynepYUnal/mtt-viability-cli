#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

INPUT_FILE="data/raw_plate_example.csv"
OUTPUT_FILE="results/viability_summary.tsv"

usage() {
    echo "Usage: $0 [-i input_plate.csv] [-o output_summary.tsv]"
    echo "  -i  Input 96-well plate CSV file (default: data/raw_plate_example.csv)"
    echo "  -o  Output summary TSV file (default: results/viability_summary.tsv)"
    exit 1
}

while getopts "i:o:h" opt; do
    case "$opt" in
        i) INPUT_FILE="$OPTARG" ;;
        o) OUTPUT_FILE="$OPTARG" ;;
        h) usage ;;
        *) usage ;;
    esac
done

if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Error: Input file '$INPUT_FILE' not found." >&2
    exit 1
fi

mkdir -p "$(dirname "$OUTPUT_FILE")"

awk -F',' '
NR == FNR {
    if ($2 == "Blank")   { b += $4; bn++ }
    if ($2 == "Control") { c += $4; cn++ }
    next
}
FNR == 1 {
    if (bn == 0 || cn == 0) {
        print "Error: Blank or Control wells missing in input file." > "/dev/stderr"
        exit 1
    }
    bm = b / bn
    cn_net = (c / cn) - bm
    next
}
$2 != "Blank" {
    net = $4 - bm
    printf "%s\t%s\t%.4f\n", $2, $3, (net / cn_net) * 100
}
' "$INPUT_FILE" "$INPUT_FILE" \
| awk -F'\t' '
{
    key = $1 "\t" $2
    n[key]++
    s[key] += $3
    sq[key] += $3 * $3
}
END {
    for (k in n) {
        mean = s[k] / n[k]
        sd = (n[k] > 1) ? sqrt((sq[k] - (s[k]^2) / n[k]) / (n[k] - 1)) : 0
        printf "%s\t%d\t%.2f\t%.2f\n", k, n[k], mean, sd
    }
}
' \
| sort -t$'\t' -k2,2n \
| awk 'BEGIN { print "Group\tDose_uM\tN\tMean_Viability_Pct\tSD" } { print }' \
> "$OUTPUT_FILE"

echo "Analysis complete. Summary saved to: $OUTPUT_FILE"
cat "$OUTPUT_FILE"

PLOT_FILE="${OUTPUT_FILE%.*}.png"
PYTHON_BIN=".venv/bin/python3"
[[ ! -x "$PYTHON_BIN" ]] && PYTHON_BIN="python3"

"$PYTHON_BIN" scripts/fit_ic50.py "$OUTPUT_FILE" "$PLOT_FILE"
