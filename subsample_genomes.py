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

        # Calculate the maximum possible number of fragments for this file
        max_fragments = len(combined_seq) // fragment_length
        if max_fragments == 0:
            print(f"File {file} combined sequence length is less than the fragment length. Skipping this file.")
            continue

        # Use the smaller of the user-specified number of fragments and the maximum possible number
        actual_fragments = min(n_fragments, max_fragments)

        start_indices = random.sample(range(len(combined_seq) - fragment_length + 1), actual_fragments)
        fragments = [combined_seq[i: i + fragment_length] for i in start_indices]

        with open(output_file, 'w') as f:
            for i, fragment in enumerate(fragments):
                f.write(f'>{file}_{i}\n')
                f.write(str(fragment) + '\n')

        print(f"Successfully generated {len(fragments)} fragments, written to {output_file}")

