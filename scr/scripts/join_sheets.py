#!/usr/bin/env python3
"""
Script to join CleanData and KA sheets on KB_Article_ID column.
Creates a new sheet 'FinalCleanData' with all CleanData columns plus new columns from KA.
"""

import pandas as pd
import openpyxl
from pathlib import Path

def join_sheets():
    # Define the Excel file path
    excel_file = Path(__file__).parent.parent.parent / "FinalData.xlsx"

    print(f"Reading Excel file: {excel_file}")

    # Load both sheets
    clean_data = pd.read_excel(excel_file, sheet_name='CleanData')
    ka_data = pd.read_excel(excel_file, sheet_name='KA')

    print(f"\nCleanData shape: {clean_data.shape}")
    print(f"CleanData columns: {list(clean_data.columns)}")
    print(f"\nKA shape: {ka_data.shape}")
    print(f"KA columns: {list(ka_data.columns)}")

    # Check if KB_Article_ID exists in both sheets
    if 'KB_Article_ID' not in clean_data.columns:
        raise ValueError("KB_Article_ID column not found in CleanData sheet")
    if 'KB_Article_ID' not in ka_data.columns:
        raise ValueError("KB_Article_ID column not found in KA sheet")

    # Perform left join to keep all CleanData records and add ALL KA columns
    # Use suffixes to distinguish overlapping columns (except KB_Article_ID)
    final_data = clean_data.merge(
        ka_data,
        on='KB_Article_ID',
        how='left',
        suffixes=('_CleanData', '_KA')
    )

    print(f"\nColumns added from KA: {list(ka_data.columns)}")

    print(f"\nFinal data shape: {final_data.shape}")
    print(f"Final data columns: {list(final_data.columns)}")

    # Load the workbook to add a new sheet
    print(f"\nWriting to new sheet 'FinalCleanData'...")

    with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        final_data.to_excel(writer, sheet_name='FinalCleanData', index=False)

    print(f"✓ Successfully created 'FinalCleanData' sheet with {len(final_data)} rows")
    print(f"✓ Total columns: {len(final_data.columns)}")

if __name__ == "__main__":
    try:
        join_sheets()
    except Exception as e:
        print(f"Error: {e}")
        raise
