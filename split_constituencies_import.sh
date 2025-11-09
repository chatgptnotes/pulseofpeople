#!/bin/bash

# Split the large constituencies SQL into 3 manageable batches
# Each batch: ~78 constituencies

INPUT_FILE="supabase/migrations/20251109140000_insert_all_234_constituencies.sql"
OUTPUT_DIR="supabase/migrations/batches"

mkdir -p "$OUTPUT_DIR"

echo "🔧 Splitting constituencies into 3 batches..."

# Extract header and organization insert
head -17 "$INPUT_FILE" > "$OUTPUT_DIR/batch1_header.sql"

# Split the VALUES part into 3 equal parts
# This is complex, so we'll use a simpler approach: split by line count

TOTAL_LINES=$(wc -l < "$INPUT_FILE")
LINES_PER_BATCH=$((TOTAL_LINES / 3))

# Batch 1: Lines 1 to LINES_PER_BATCH
head -$LINES_PER_BATCH "$INPUT_FILE" > "$OUTPUT_DIR/batch1_constituencies.sql"

# Batch 2: Lines LINES_PER_BATCH+1 to 2*LINES_PER_BATCH  
tail -n +$((LINES_PER_BATCH + 1)) "$INPUT_FILE" | head -$LINES_PER_BATCH > "$OUTPUT_DIR/batch2_constituencies.sql"

# Batch 3: Remaining lines
tail -n +$((2 * LINES_PER_BATCH + 1)) "$INPUT_FILE" > "$OUTPUT_DIR/batch3_constituencies.sql"

echo "✅ Split complete!"
echo "   Batch 1: $OUTPUT_DIR/batch1_constituencies.sql"
echo "   Batch 2: $OUTPUT_DIR/batch2_constituencies.sql"
echo "   Batch 3: $OUTPUT_DIR/batch3_constituencies.sql"

