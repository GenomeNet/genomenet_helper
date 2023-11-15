import os
import subprocess
from Bio import SeqIO
import pandas as pd
import tempfile
import random
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)

def harmonize_kmer_headers(file1, file2):
    # Load the CSV files
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Get the union of k-mer columns from both files
    kmer_cols = sorted(set(df1.columns) | set(df2.columns))

    # Rearrange and fill missing k-mers with 0s
    df1 = df1.reindex(columns=['unique_id', 'file_name', 'sample_id', 'class'] + kmer_cols, fill_value=0)
    df2 = df2.reindex(columns=['unique_id', 'file_name', 'sample_id', 'class'] + kmer_cols, fill_value=0)

    # Save the harmonized files
    df1.to_csv(file1.replace('.csv', '_harmonized.csv'), index=False)
    df2.to_csv(file2.replace('.csv', '_harmonized.csv'), index=False)

def process_fasta(fasta_path, max_subseqs=20, kmer_size=7, subsequence_size=2000, temp_dir="", random_mode=False):
    output_files = []
    total_seq = 0

    for record in SeqIO.parse(fasta_path, "fasta"):
        seq_str = str(record.seq)

        # Calculate non-overlapping subsequence start indices
        subseq_start_indices = range(0, len(seq_str), subsequence_size)
        
        if random_mode:
            # Calculate the maximum number of non-overlapping subsequences
            max_possible_subseqs = len(subseq_start_indices)
            # Select a random sample without overlapping
            chosen_indices = random.sample(subseq_start_indices, min(max_subseqs, max_possible_subseqs))
        else:
            # Use the first 'max_subseqs' subsequences
            chosen_indices = list(subseq_start_indices)[:max_subseqs]

        subseqs = [seq_str[i:i+subsequence_size] for i in chosen_indices]
        total_seq += len(subseqs)

        for idx, subseq in enumerate(subseqs):
            subseq_file = os.path.join(temp_dir, f"subseq_{idx}.fasta")
            with open(subseq_file, "w") as f:
                f.write(f">subseq_{idx}\n{subseq}")
            run_jellyfish(subseq_file, kmer_size, temp_dir)
            output_files.append(os.path.join(temp_dir, f"{os.path.basename(subseq_file).replace('.fasta', '')}_jf_formatted.csv"))
    
    logging.info(f"Processed {total_seq} sequences from {fasta_path}")
    return output_files


def run_jellyfish(fasta_path, kmer_size, temp_dir):
    output_prefix = os.path.join(temp_dir, os.path.basename(fasta_path).replace('.fasta', '') + '_jf')
    command = f"jellyfish count -m {kmer_size} -o {output_prefix} -s 10000000 -t 20 {fasta_path}"
    try:
        subprocess.run(command, shell=True, check=True)
        logging.info(f'Jellyfish completed for {fasta_path}')
    except subprocess.CalledProcessError:
        logging.error(f'Jellyfish failed for {fasta_path}')
    dump_command = f"jellyfish dump {output_prefix} > {output_prefix}_dump.fa"
    subprocess.run(dump_command, shell=True)
    reformat_jellyfish_dump(f"{output_prefix}_dump.fa")

def reformat_jellyfish_dump(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    output_file = file_path.replace('_dump.fa', '_formatted.csv')
    with open(output_file, 'w') as file:
        for i in range(0, len(lines), 2):
            count, sequence = lines[i].strip('>\n'), lines[i+1].strip()
            file.write(f'{sequence},{count}\n')

def aggregate_jellyfish_output(fasta_path, output_files, class_):
    aggregated_data = []
    for idx, file in enumerate(output_files):
        df = pd.read_csv(file, header=None, names=['kmer', 'count'])
        unique_id = f"{os.path.splitext(os.path.basename(fasta_path))[0]}_chunk_{idx+1}"
        data = {'unique_id': unique_id, 'file_name': os.path.basename(fasta_path), 'sample_id': idx+1, 'class': class_}
        data.update(df.set_index('kmer')['count'].to_dict())
        aggregated_data.append(data)
    result_df = pd.DataFrame(aggregated_data).fillna(0)
    result_df.to_csv(f"{os.path.splitext(os.path.basename(fasta_path))[0]}_aggregated_jellyfish_output.csv", index=False)

def process_kmer_profiles(input_dir, kmer_size, max_subseqs, subsequence_size, random_mode, label=""):
    all_aggregated_data = []
    fasta_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.fasta')]
    
    for fasta_file in fasta_files:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_files = process_fasta(fasta_file, max_subseqs, kmer_size, subsequence_size, temp_dir, random_mode)
            aggregate_jellyfish_output(fasta_file, output_files, label)
            result_file = f"{os.path.splitext(os.path.basename(fasta_file))[0]}_aggregated_jellyfish_output.csv"
            all_aggregated_data.append(pd.read_csv(result_file))

    if all_aggregated_data:
        combined_df = pd.concat(all_aggregated_data, ignore_index=True)
        output_file_path = f"{os.path.basename(input_dir)}_all_aggregated_jellyfish_output.csv"
        combined_df.to_csv(output_file_path, index=False)
        logging.info(f"K-mer profiling completed. Output file saved as: {output_file_path}")