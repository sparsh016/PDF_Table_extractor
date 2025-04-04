import fitz
import pandas as pd
import numpy as np
from collections import defaultdict

def extract_tables_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    all_tables = []
    
    for page in doc:
        text_blocks = page.get_text("blocks")
        text_blocks = [b for b in text_blocks if b[6] == 0]  # Remove image blocks
        text_blocks.sort(key=lambda b: (b[1], b[0]))

        # Dynamic row grouping
        y_coords = [b[1] for b in text_blocks]
        y_threshold = np.median(np.diff(sorted(y_coords))) / 2 if len(y_coords) > 1 else 3

        rows = defaultdict(list)
        current_y = None
        for block in text_blocks:
            if current_y is None or abs(block[1] - current_y) > y_threshold:
                current_y = block[1]
            rows[current_y].append(block)

        # Column detection
        table = []
        for y in sorted(rows.keys()):
            row_blocks = sorted(rows[y], key=lambda b: b[0])
            
            # Calculate dynamic column gaps
            if len(row_blocks) > 1:
                gaps = [row_blocks[i+1][0] - row_blocks[i][2] 
                       for i in range(len(row_blocks)-1)]
                median_gap = np.median(gaps) if gaps else 0
                col_threshold = median_gap * 1.5 if median_gap > 0 else 5
            else:
                col_threshold = 5

            # Merge columns
            row = []
            prev_right = -float('inf')
            for b in row_blocks:
                if b[0] - prev_right > col_threshold:
                    row.append(b[4].strip())
                else:
                    row[-1] += " " + b[4].strip()
                prev_right = b[2]

            # Filter non-table content
            if (len(row) > 1 and 
                not any(s in cell for cell in row 
                       for s in ["***END", "Page No:", "BANK NAME"])):
                table.append(row)

        # Merge with previous tables if column count matches
        if table:
            if all_tables and len(table[0]) == len(all_tables[-1][0]):
                all_tables.extend(table)
            else:
                all_tables.append(table)

    doc.close()
    return all_tables[0] if all_tables else []

# Rest of the code remains similar