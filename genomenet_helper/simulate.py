import os
import random
import collections
from collections import defaultdict
import numpy as np
from Bio import SeqIO
from .utils import generate_output_directory

def calculate_frequencies(fasta_file, kmer_length):
    records = list(SeqIO.parse(fasta_file, "fasta"))
    sequence = str(records[0].seq).upper()

    # Check for non-ACGT characters and print a message if found
    non_acgt_characters = set([base for base in sequence if base not in 'ACGT'])
    if non_acgt_characters:
        non_acgt_char_list = ', '.join(non_acgt_characters)
        print(f"Warning: Non-ACGT characters detected in {os.path.basename(fasta_file)} ({non_acgt_char_list}). These will be excluded from k-mer frequencies.")

    # Filter out non-ACGT characters
    filtered_sequence = ''.join([base for base in sequence if base in 'ACGT'])

    counter = collections.Counter([filtered_sequence[i:i+kmer_length] for i in range(len(filtered_sequence) - kmer_length + 1)])
    total = sum(counter.values())
    kmers = list(counter.keys())
    probabilities = [counter[kmer] / total for kmer in kmers]
    return kmers, probabilities, counter

def add_randomness(probabilities, randomness):
    new_probabilities = [p + np.random.uniform(-randomness, randomness) for p in probabilities]
    total = sum(new_probabilities)
    new_probabilities = [p / total for p in new_probabilities]
    return new_probabilities


def simulate_genomes(input_dir, sim_size_kb=100, kmer_length=3, seed=None, randomness=0.0, monitor_kmers=None):
    random.seed(seed)
    
    output_dir = generate_output_directory(input_dir, "simulated")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    num_files_written = 0
    lengths = []
    print("Frequencies for selected k-mers for the first 10 processed files:")
    for fasta_file in os.listdir(input_dir):
        if fasta_file.endswith('.fasta'):
            input_path = os.path.join(input_dir, fasta_file)

            mean_length = sim_size_kb * 1000  # Convert kb to bases
            std_dev = sim_size_kb * 1000 * 0.10  # 10% of sim_size_kb in bases
            # This means that roughly 68% of the sequences would be within 90kb to 110kb, 95% would be within 80kb to 120kb, and almost all should fall between 70kb and 130kb if the lengths are normally distributed.

            kmers, probabilities, kmer_counts = calculate_frequencies(input_path, kmer_length)
            if num_files_written < 10 and monitor_kmers:
                frequencies = {kmer: kmer_counts.get(kmer, 0) / sum(kmer_counts.values()) for kmer in monitor_kmers}
                print(f"Frequencies in {fasta_file}: " + ", ".join([f"{kmer}: {freq:.4f}" for kmer, freq in frequencies.items()]))

            seq_length = int(np.random.normal(mean_length, std_dev))
            lengths.append(seq_length)
            new_probabilities = add_randomness(probabilities, randomness)
            
            sequence = ''.join(random.choices(kmers, weights=new_probabilities, k=seq_length // kmer_length))
            
            header = f'>simulated_sequence_{num_files_written + 1}'
            filename = os.path.join(output_dir, f'simulated_sequence_{num_files_written + 1}.fasta')

            with open(filename, 'w') as f:
                f.write(header + '\n')
                f.write(sequence)

            num_files_written += 1

    print(f'Finished generating {num_files_written} simulated genomes in {output_dir}.')
    print(f'Average sequence length: {np.mean(lengths):.2f} ± {np.std(lengths):.2f}')
    print(f'Min sequence length: {min(lengths)}')
    print(f'Max sequence length: {max(lengths)}')
