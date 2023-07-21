import random
import collections
import numpy as np
import os
from Bio import SeqIO

def calculate_frequencies(fasta_file, kmer_length):
    records = list(SeqIO.parse(fasta_file, "fasta"))
    sequence = str(records[0].seq).upper()
    counter = collections.Counter([sequence[i:i+kmer_length] for i in range(len(sequence) - kmer_length + 1)])
    total = sum(counter.values())
    kmers = list(counter.keys())
    probabilities = [counter[kmer] / total for kmer in kmers]
    return kmers, probabilities, counter

def add_randomness(probabilities, randomness):
    new_probabilities = [p + np.random.uniform(-randomness, randomness) for p in probabilities]
    total = sum(new_probabilities)
    new_probabilities = [p / total for p in new_probabilities]
    return new_probabilities

def simulate_genome(num_file, sample_from, kmer_length, seed, output_dir, randomness):
    random.seed(seed)

    mean_length = 10**6
    std_dev = 10**5

    if sample_from:
        kmers, probabilities, counter = calculate_frequencies(sample_from, kmer_length)
        print(f'Sampled {kmer_length}-mer frequencies:')
        for kmer, freq in counter.items():
            print(f'{kmer}: {freq / sum(counter.values()):.4f}')
    else:
        kmers, probabilities = ['A', 'C', 'G', 'T'], [0.25, 0.25, 0.25, 0.25]
        print('Nucleotide frequencies: A: 0.25, C: 0.25, G: 0.25, T: 0.25')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    else:
        print(f'Warning: Output directory {output_dir} already exists. Existing files may be overwritten.')

    for i in range(1, num_file + 1):
        print(f'Generating file {i} of {num_file}')

        seq_length = int(np.random.normal(mean_length, std_dev))
        new_probabilities = add_randomness(probabilities, randomness)

        sequence = ''.join(random.choices(kmers, weights=new_probabilities, k=seq_length // kmer_length))

        header = f'>random_sequence_{i}'
        filename = f'{output_dir}/{seed if seed else "random"}_random_sequence_{i}_{"sampled" if sample_from else "default"}_{kmer_length}mer.fasta'

        with open(filename, 'w') as f:
            f.write(header + '\n')
            f.write(sequence)

    print('Finished generating .FASTA files.')

