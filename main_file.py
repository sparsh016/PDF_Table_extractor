import fitz
import pandas as pd
import numpy as np
from collections import defaultdict

def extract_tables_from_pdf(pdf_path):
    """
    Extract tables from PDF using spatial layout analysis
    Returns: List of tables (each table is list of rows)
    """
    doc = fitz.open(pdf_path)
    tables = []
    current_table = []

    for page in doc:
        # Get text blocks with coordinates
        blocks = page.get_text("blocks", sort=True)
        blocks = [b for b in blocks if b[6] == 0]  # Remove image blocks

        # Cluster blocks into rows using y-coordinates
        y_coords = sorted(list({b[1] for b in blocks}))
        y_threshold = np.median(np.diff(y_coords)) if len(y_coords) > 1 else 10

        rows = defaultdict(list)
        for block in blocks:
            y = min(y_coords, key=lambda y: abs(y - block[1]))
            rows[y].append(block)

        # Process each row
        for y in sorted(rows.keys()):
            row_blocks = sorted(rows[y], key=lambda b: b[0])
            
            # Calculate column gaps
            gaps = [row_blocks[i+1][0] - row_blocks[i][2] 
                    for i in range(len(row_blocks)-1)]
            col_threshold = np.median(gaps) * 1.2 if gaps else 5

            # Merge cells into columns
            row = []
            prev_right = -np.inf
            current_cell = ""
            for b in row_blocks:
                if b[0] - prev_right > col_threshold:
                    if current_cell:
                        row.append(current_cell.strip())
                    current_cell = b[4].strip()
                else:
                    current_cell += " " + b[4].strip()
                prev_right = b[2]
            if current_cell:
                row.append(current_cell.strip())

            # Filter non-table rows
            if is_table_row(row):
                if current_table and len(row) != len(current_table[0]):
                    # Column count changed - finalize current table
                    tables.append(current_table)
                    current_table = []
                current_table.append(row)
            elif current_table:
                # End of table
                tables.append(current_table)
                current_table = []

        # Handle table continuing to next page
        if current_table and tables and len(current_table[0]) == len(tables[-1][0]):
            tables[-1].extend(current_table)
            current_table = []

    if current_table:
        tables.append(current_table)

    doc.close()
    return tables

def is_table_row(row):
    """Determine if a row belongs to a table"""
    if len(row) < 2:
        return False
    excluded_phrases = [
        "BANK NAME", "Page No:", "***END", "REPORT PRINTED BY",
        "Statement of account", "Grand Total:", "NOTE:"
    ]
    return not any(phrase in cell for cell in row for phrase in excluded_phrases)

def save_tables_to_excel(tables, output_path):
    """Save extracted tables to Excel with multiple sheets"""
    with pd.ExcelWriter(output_path) as writer:
        for i, table in enumerate(tables):
            if len(table) < 2:
                continue  # Skip single-row tables
                
            # Try to detect header row
            header = table[0] if is_header(table[0], table[1]) else None
            data = table[1:] if header else table
            
            df = pd.DataFrame(data, columns=header or None)
            sheet_name = f"Table_{i+1}"
            df.to_excel(writer, sheet_name=sheet_name, index=False)

def is_header(header_row, first_data_row):
    """Check if a row is likely a table header"""
    if len(header_row) != len(first_data_row):
        return False
    # Check for typical header characteristics
    return any(char.isupper() for cell in header_row for char in cell)

if __name__ == "__main__":
    input_pdfs = ["test3 (1) (1).pdf", "test6 (1) (1).pdf"]
    
    for pdf_path in input_pdfs:
        tables = extract_tables_from_pdf(pdf_path)
        output_file = pdf_path.replace(".pdf", "_output.xlsx")
        save_tables_to_excel(tables, output_file)
        print(f"Processed {pdf_path}. Created {output_file} with {len(tables)} tables.")
