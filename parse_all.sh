#!/usr/bin/env bash
set -eo pipefail

RAW_DIR="data/raw_documents"
OUTPUT_DIR="data/output"
DETAILS_SUBDIR="details"

# Collect summary rows
ROWS=()

for filepath in "$RAW_DIR"/*.*; do
  fname=$(basename "$filepath")
  dt=""

  # Infer doc_type
  case "$fname" in
    [Ii]nvoice* )            dt="invoice" ;;
    *[Rr]eceipt* )           dt="receipt" ;;
    [Ww]2* )                 dt="w2" ;;
    seller-statement*|sellers-statement* )
                             dt="seller-statement" ;;
    * )
      echo "⚠️  Skipping unknown file type: $fname"
      continue
      ;;
  esac

  echo "▶️ Parsing '$fname' as $dt..."
  python -m src.main "$filepath" "$dt"

  ts=$(date -u +'%Y-%m-%dT%H:%M:%SZ')

  # Map doc_type → summary CSV path
  case "$dt" in
    invoice)           summary_csv="$OUTPUT_DIR/Invoice-List.csv" ;;
    receipt)           summary_csv="$OUTPUT_DIR/Receipt-List.csv" ;;
    w2)                summary_csv="$OUTPUT_DIR/W2-List.csv" ;;
    seller-statement)  summary_csv="$OUTPUT_DIR/Seller-Statement.csv" ;;
    *)                 summary_csv="" ;;
  esac

  # Detail CSV path
  detail_csv="$OUTPUT_DIR/$dt/$DETAILS_SUBDIR/${fname%.*}_$dt.csv"

  if [ -n "$summary_csv" ]; then
    ROWS+=("$ts|$fname|$RAW_DIR|$dt|$summary_csv|$detail_csv")
  fi
done

# Nothing parsed?
if [ ${#ROWS[@]} -eq 0 ]; then
  echo "No documents parsed."
  exit 0
fi

# Pretty-print an ASCII table
cols=(Timestamp Filename InputDir DocType SummaryCSV DetailCSV)
declare -a W
# Compute column widths
for i in "${!cols[@]}"; do
  W[$i]=${#cols[$i]}
done
for row in "${ROWS[@]}"; do
  IFS='|' read -r ts fn idir dt scsv dcsv <<<"$row"
  items=("$ts" "$fn" "$idir" "$dt" "$scsv" "$dcsv")
  for i in "${!items[@]}"; do
    (( ${#items[$i]} > W[$i] )) && W[$i]=${#items[$i]}
  done
done

# Separator line
sep="+"
for i in "${!cols[@]}"; do
  sep+=$(printf -- "-%.0s" $(seq 1 $((W[$i]+2))))
  sep+="+"
done

# Header
echo "$sep"
line="|"
for i in "${!cols[@]}"; do
  line+=" $(printf "%-${W[$i]}s" "${cols[$i]}") |"
done
echo "$line"
echo "$sep"

# Rows
for row in "${ROWS[@]}"; do
  IFS='|' read -r ts fn idir dt scsv dcsv <<<"$row"
  items=("$ts" "$fn" "$idir" "$dt" "$scsv" "$dcsv")
  line="|"
  for i in "${!items[@]}"; do
    line+=" $(printf "%-${W[$i]}s" "${items[$i]}") |"
  done
  echo "$line"
done
echo "$sep"