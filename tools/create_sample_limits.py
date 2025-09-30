#!/usr/bin/env python3
"""
Sample script to create example limits Excel file
Run this script to generate sample_limits.xlsx
"""

import polars as pl
import numpy as np

def create_sample_file(file_path: str):
    """Örnek bir limit dosyası oluşturur."""
    try:
        # Sample data
        data = {
            'Signal_Name': ['Signal_A', 'Signal_B', 'Signal_C'],
            'Static_Upper_Limit': [95.0, 105.0, 88.0],
            'Static_Lower_Limit': [10.0, -5.0, 20.0]
        }
        
        # Create a Polars DataFrame
        df = pl.DataFrame(data)
        
        # Save to Excel
        df.write_excel(file_path, sheet_name='Limits')
        
        print(f"✅ Sample limits file created at: {file_path}")
        
    except ImportError:
        print("❌ Error: polars and openpyxl libraries are required")
        print("Install with: pip install polars openpyxl")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    try:
        create_sample_file('sample_limits.xlsx')
    except ImportError:
        print("❌ Error: pandas and openpyxl libraries are required")
        print("Install with: pip install pandas openpyxl")
    except Exception as e:
        print(f"❌ Error creating Excel file: {e}")
