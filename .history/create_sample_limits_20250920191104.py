#!/usr/bin/env python3
"""
Sample script to create example limits Excel file
Run this script to generate sample_limits.xlsx
"""

import pandas as pd

def create_sample_limits_excel():
    """Create a sample Excel file with limit configurations."""
    
    # Sample data with various parameter types
    sample_data = [
        {
            'Parameter': 'sine_1hz',
            'Warning_Min': -0.8,
            'Warning_Max': 0.8,
            'Description': 'Sine wave 1Hz signal limits'
        },
        {
            'Parameter': 'sine_2hz', 
            'Warning_Min': -0.9,
            'Warning_Max': 0.9,
            'Description': 'Sine wave 2Hz signal limits'
        },
        {
            'Parameter': 'noisy_signal',
            'Warning_Min': -1.5,
            'Warning_Max': 1.5,
            'Description': 'Noisy signal limits'
        },
        {
            'Parameter': 'temperature',
            'Warning_Min': 0,
            'Warning_Max': 85,
            'Description': 'Temperature sensor limits (Celsius)'
        },
        {
            'Parameter': 'pressure',
            'Warning_Min': 0,
            'Warning_Max': 10,
            'Description': 'Pressure sensor limits (bar)'
        },
        {
            'Parameter': 'voltage',
            'Warning_Min': 4.5,
            'Warning_Max': 5.5,
            'Description': 'Supply voltage limits (V)'
        },
        {
            'Parameter': 'current',
            'Warning_Min': 0,
            'Warning_Max': 2.5,
            'Description': 'Current consumption limits (A)'
        },
        {
            'Parameter': 'rpm',
            'Warning_Min': 0,
            'Warning_Max': 3000,
            'Description': 'Motor RPM limits'
        },
        {
            'Parameter': 'vibration',
            'Warning_Min': 0,
            'Warning_Max': 5,
            'Description': 'Vibration level limits (g)'
        },
        {
            'Parameter': 'flow_rate',
            'Warning_Min': 0,
            'Warning_Max': 100,
            'Description': 'Flow rate limits (L/min)'
        }
    ]
    
    # Create DataFrame
    df = pd.DataFrame(sample_data)
    
    # Save to Excel with formatting
    with pd.ExcelWriter('sample_limits.xlsx', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Limits', index=False)
        
        # Get the workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Limits']
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print("✅ Sample limits Excel file created: sample_limits.xlsx")
    print("\n📋 File contains the following columns:")
    print("- Parameter: Name of the signal/parameter")
    print("- Warning_Min: Minimum warning limit value")  
    print("- Warning_Max: Maximum warning limit value")
    print("- Description: Optional description of the parameter")
    print("\n🔧 Usage:")
    print("1. Open sample_limits.xlsx in Excel")
    print("2. Modify the Warning_Min and Warning_Max values as needed")
    print("3. Add/remove parameters as required")
    print("4. Save the file")
    print("5. Use 'Import from Excel' button in Static Limits panel")

if __name__ == "__main__":
    try:
        create_sample_limits_excel()
    except ImportError:
        print("❌ Error: pandas and openpyxl libraries are required")
        print("Install with: pip install pandas openpyxl")
    except Exception as e:
        print(f"❌ Error creating Excel file: {e}")
