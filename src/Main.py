import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend to avoid Tkinter issues
import matplotlib.pyplot as plt

def process_csv(file_path):
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        return

    # Strip carriage returns from column names
    df.columns = [str(col).replace('\r', '').replace('\n', '').strip() for col in df.columns]

    # Strip carriage returns and whitespace from string columns
    for col in df.select_dtypes(include=['object', 'string']).columns:
        df[col] = df[col].astype(str).str.replace(r'[\r\n]', '', regex=True).str.strip()

    # Ignore 'ID' column if present
    if 'ID' in df.columns:
        df = df.drop(columns=['ID'])

    # Select only numeric columns for these calculations
    numeric_df = df.select_dtypes(include=[np.number])
    
    if numeric_df.empty:
        print("No numeric columns found in the CSV to calculate statistics.")
        return

    print(f"Loaded '{file_path}' successfully.")
    print(f"Found {len(numeric_df.columns)} numeric variables to analyze.")
    print("--- Statistical Analysis ---")
    
    # Create an output directory for plots based on the CSV filename
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    plots_dir = f"{base_name}_plots"
    os.makedirs(plots_dir, exist_ok=True)
    print(f"Box plots will be saved in the directory: {plots_dir}")

    for column in numeric_df.columns:
        print(f"\n[{column}]")
        col_data = numeric_df[column].dropna()
        
        if col_data.empty:
            print("  No valid data available.")
            continue
            
        # Arithmetic mean
        mean = col_data.mean()
        print(f"  Arithmetic mean:           {mean:.4f}")
        
        # Median
        median = col_data.median()
        print(f"  Median:                    {median:.4f}")
        
        # Mode
        mode_series = col_data.mode()
        if not mode_series.empty:
            modes = ", ".join([f"{m:.4f}" for m in mode_series])
            print(f"  Mode:                      {modes}")
        else:
            print("  Mode:                      None")
            
        # Sample variance (ddof=1 is default in pandas)
        variance = col_data.var()
        print(f"  Sample variance:           {variance:.4f}")
        
        # Standard deviation (ddof=1 is default in pandas)
        std_dev = col_data.std()
        print(f"  Standard deviation:        {std_dev:.4f}")
        
        # Coefficient of variation
        # Handled mean == 0 to avoid division by zero
        if mean != 0:
            cv = (std_dev / mean) * 100
            print(f"  Coefficient of variation:  {cv:.4f}%")
        else:
            print("  Coefficient of variation:  Undefined (mean is 0)")
            
        # Coefficient of kurtosis
        kurtosis = col_data.kurtosis()
        if pd.isna(kurtosis):
            print("  Coefficient of kurtosis:   Not enough data")
        else:
            print(f"  Coefficient of kurtosis:   {kurtosis:.4f}")
            
        # Box plot
        plt.figure(figsize=(6, 4))
        plt.boxplot(col_data, vert=False, patch_artist=True)
        plt.title(f'Box Plot of {column}')
        plt.xlabel('Values')
        
        # Sanitize column name for filename
        safe_col_name = "".join([c if c.isalnum() else "_" for c in str(column)])
        plot_filename = os.path.join(plots_dir, f"boxplot_{safe_col_name}.png")
        
        plt.tight_layout()
        plt.savefig(plot_filename)
        plt.close()
        print(f"  Box plot saved to:         {plot_filename}")

        # Frequency chart generation removed per request

    categorical_df = df.select_dtypes(exclude=[np.number])
    if not categorical_df.empty:
        print("\n--- Categorical Analysis ---")
        for column in categorical_df.columns:
            print(f"\n[{column}]")
            col_data = categorical_df[column].dropna()
            
            if col_data.empty:
                print("  No valid data available.")
                continue
                
            # Mode
            mode_series = col_data.mode()
            if not mode_series.empty:
                modes = ", ".join([str(m) for m in mode_series])
                print(f"  Mode:                      {modes}")
            else:
                print("  Mode:                      None")
                
            # Value counts / Frequencies
            value_counts = col_data.value_counts()
            print("  Frequencies:")
            for val, count in value_counts.items():
                print(f"    {val}: {count}")


path = os.path.join("data", "test_dataset.csv")
process_csv(path)