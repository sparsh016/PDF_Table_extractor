



--> For test3 (1) (1).pdf:

1. Extracted transaction table with columns: Date, Transaction Description, Debit/Credit, Amount, Balance

2. Contains all transaction entries from the statement

3. Output saved to test3 (1) (1)_output.xlsx

--> For test6 (1) (1).pdf:

1. Extracted main transaction table with 10 columns matching the PDF headers

2. Includes all 100+ transactions from the 18-page statement

3. Output saved to test6 (1) (1)_output.xlsx








--------->>>>PDF Table Extractor using PyMuPDF (fitz) <<<<<<<---------

This script extracts structured table data from PDF files using the PyMuPDF (fitz) library. It intelligently groups text into rows and columns and returns it as a list of rows or a pandas DataFrame.

📌 Features
Dynamically detects and groups text blocks into table rows and columns.

Works with scanned or unstructured PDF content that includes tables.

Removes non-table text like footers or irrelevant data (e.g., page numbers, headers).

Automatically merges columns that were split due to layout gaps.

🧠 How It Works
The function extract_tables_from_pdf(pdf_path) works in several steps:

1. Load the PDF

doc = fitz.open(pdf_path)
Uses PyMuPDF to open and read the PDF file page by page.

2. Extract Text Blocks

text_blocks = page.get_text("blocks")
Gets all text blocks on a page. Filters out image blocks using b[6] == 0.

3. Group Text by Rows (Y-axis Clustering)

y_coords = [b[1] for b in text_blocks]
y_threshold = ...
rows = defaultdict(list)
Calculates vertical spacing between blocks to group them into rows based on Y-coordinates.

4. Group Text into Columns

row_blocks.sort(key=lambda b: b[0])
Sorts text blocks within each row by X-coordinate and merges nearby blocks based on horizontal spacing (X-axis).

5. Filter Non-Table Content

if (len(row) > 1 and not any(s in cell for cell in row for s in ["***END", "Page No:", "BANK NAME"])):
    table.append(row)
Filters out known non-table content like footers and page markers.

6. Merge Tables

if all_tables and len(table[0]) == len(all_tables[-1][0]):
    all_tables.extend(table)
If consecutive tables have the same number of columns, they are merged into one.

7. Return the Extracted Table

return all_tables[0] if all_tables else []
Returns the first table found in the PDF.

✅ Example Output
Each row is returned as a list of strings:


[
    ["Subject", "Grade", "Credits"],
    ["Math", "A", "4"],
    ["Physics", "B+", "3"],
    ...
]
You can also convert it to a DataFrame:


import pandas as pd
df = pd.DataFrame(table[1:], columns=table[0])
🛠️ Dependencies
Install the required libraries with:


pip install pymupdf pandas numpy
📂 Usage

from extract_pdf_tables import extract_tables_from_pdf

pdf_path = "your_pdf_file.pdf"
table = extract_tables_from_pdf(pdf_path)
