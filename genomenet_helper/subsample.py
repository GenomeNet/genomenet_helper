import os
import random
from Bio import SeqIO
from .utils import generate_output_directory

def sample_fasta_files(input_file, output_dir, fragment_length, n_fragments):
    """
    This function subsamples the fasta file to produce n_fragments of size fragment_length.
    For simplicity, I'm assuming each fasta file contains one sequence, 
    and I'm generating non-overlapping fragments.
    """
    records = list(SeqIO.parse(input_file, "fasta"))
    sequence = str(records[0].seq).upper()

    # Compute total number of possible fragments of size fragment_length.
    total_fragments = len(sequence) // fragment_length

    # Randomly select n_fragments.
    selected_fragments = set()
    while len(selected_fragments) < min(n_fragments, total_fragments):
        selected_fragments.add(random.randint(0, total_fragments - 1))

    # Save these fragments to new fasta files.
    for idx, fragment_index in enumerate(selected_fragments):
        start = fragment_index * fragment_length
        end = start + fragment_length

        header = f'>subsample_{idx}'
        filename = os.path.join(output_dir, f'subsample_{idx}.fasta')

        with open(filename, 'w') as f:
            f.write(header + '\n')
            f.write(sequence[start:end])

def subsample_genomes(input_dir, fragment_length=4000, n_fragments=2500):
    output_dir = generate_output_directory(input_dir, "subsampled")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Subsample each fasta file in the input directory.
    for fasta_file in os.listdir(input_dir):
        if fasta_file.endswith('.fasta'):
            input_file = os.path.join(input_dir, fasta_file)
            sample_fasta_files(input_file, output_dir, fragment_length, n_fragments)

    print(f'Successfully subsampled genomes, written to {output_dir}')