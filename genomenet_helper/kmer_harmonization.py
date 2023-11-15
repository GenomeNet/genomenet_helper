import pandas as pd

def harmonize_kmer_headers(*file_paths):
    # Load all CSV files into dataframes
    dataframes = [pd.read_csv(file) for file in file_paths]

    # Get the union of k-mer columns from all files
    kmer_cols = sorted(set.union(*(set(df.columns) - {'unique_id', 'file_name', 'sample_id', 'class'} for df in dataframes)))

    # Rearrange and fill missing k-mers with 0s, then overwrite the original file
    for df, file in zip(dataframes, file_paths):
        # Ensure only k-mer columns that are missing are added
        missing_cols = [col for col in kmer_cols if col not in df.columns]
        df = df.reindex(columns=df.columns.tolist() + missing_cols, fill_value=0)

        # Reorder all columns to match the sorted k-mer list
        non_kmer_cols = ['unique_id', 'file_name', 'sample_id', 'class']
        df = df[non_kmer_cols + kmer_cols]

        # Save the harmonized dataframe
        df.to_csv(file, index=False)
