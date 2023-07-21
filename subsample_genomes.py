import os
import random
from Bio import SeqIO

def sample_fasta_files(input_dir, output_dir, fragment_length, n_fragments):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    files = [file for file in os.listdir(input_dir) if file.endswith('.fasta')]
    n_files = len(files)

    for i, file in enumerate(files, 1):
        print(f"Processing file {i}/{n_files}")
        input_file = os.path.join(input_dir, file)
        output_file = os.path.join(output_dir, file)

        combined_seq = "".join(str(record.seq) for record in SeqIO.parse(input_file, 'fasta'))

        if len(combined_seq) < fragment_length * n_fragments:
            print(f"File {file} combined sequence length is less than required for sampling. Skipping this file.")
            continue

        start_indices = random.sample(range(len(combined_seq) - fragment_length + 1), min(n_fragments, len(combined_seq) - fragment_length + 1))
        fragments = [combined_seq[i: i + fragment_length] for i in start_indices]

        with open(output_file, 'w') as f:
            for i, fragment in enumerate(fragments):
                f.write(f'>{file}_{i}\n')
                f.write(str(fragment) + '\n')

        print(f"Successfully generated {len(fragments)} fragments, written to {output_file}")
