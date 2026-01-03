import pandas as pd
import glob
from datetime import datetime

def concatenate_fbi_csvs():
    """Concatenate all FBI article links CSV files into one DataFrame"""
    
    # Find all FBI article links CSV files in the data directory
    csv_pattern = "data/fbi_article_links_*.csv"
    csv_files = glob.glob(csv_pattern)
    
    print(f"Found {len(csv_files)} CSV files to concatenate:")
    for file in csv_files:
        print(f"  - {file}")
    
    if not csv_files:
        print("No FBI article links CSV files found!")
        return
    
    # Read and concatenate all CSV files
    dfs = []
    total_rows = 0
    
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            print(f"  Loaded {file}: {len(df)} rows")
            dfs.append(df)
            total_rows += len(df)
        except Exception as e:
            print(f"  Error loading {file}: {e}")
    
    if not dfs:
        print("No valid CSV files to concatenate!")
        return
    
    # Concatenate all DataFrames
    combined_df = pd.concat(dfs, ignore_index=True)
    print(f"\nTotal rows before deduplication: {len(combined_df)}")
    
    # Remove duplicates based on URL (keep first occurrence)
    combined_df = combined_df.drop_duplicates(subset=['URL'], keep='first')
    print(f"Total rows after deduplication: {len(combined_df)}")
    
    # Save combined DataFrame
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"data/fbi_article_links_combined_{timestamp}.csv"
    combined_df.to_csv(output_filename, index=False)
    
    print(f"\n✅ Successfully concatenated {len(csv_files)} files")
    print(f"📊 Final dataset: {len(combined_df)} unique article links")
    print(f"💾 Saved to: {output_filename}")
    
    # Show sample of data
    print(f"\n📋 Sample of combined data:")
    print(f"Columns: {list(combined_df.columns)}")
    print(f"First few URLs:")
    for i, url in enumerate(combined_df['URL'].head(3)):
        print(f"  {i+1}. {url}")
    
    # Show page source distribution if available
    if 'Page_Source' in combined_df.columns:
        print(f"\n📊 Page source distribution:")
        page_counts = combined_df['Page_Source'].value_counts().sort_index()
        for page, count in page_counts.head(10).items():
            print(f"  Page {page}: {count} links")
        if len(page_counts) > 10:
            print(f"  ... and {len(page_counts) - 10} more pages")
    
    return combined_df

if __name__ == "__main__":
    concatenate_fbi_csvs()