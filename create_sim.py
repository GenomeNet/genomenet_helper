import random
import argparse
import collections
import numpy as np
import os
from Bio import SeqIO

def calculate_frequencies(fasta_file, kmer_length):
    # Read .fasta file and calculate nucleotide frequencies
    records = list(SeqIO.parse(fasta_file, "fasta"))
    sequence = str(records[0].seq).upper()
    counter = collections.Counter([sequence[i:i+kmer_length] for i in range(len(sequence) - kmer_length + 1)])
    total = sum(counter.values())
    kmers = list(counter.keys())
    probabilities = [counter[kmer] / total for kmer in kmers]
    return kmers, probabilities, counter

def add_randomness(probabilities, randomness):
    # Add a small random value to each probability
    new_probabilities = [p + np.random.uniform(-randomness, randomness) for p in probabilities]
    # Normalize to make sure they add up to 1
    total = sum(new_probabilities)
    new_probabilities = [p / total for p in new_probabilities]
    return new_probabilities

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Generate random .FASTA files.')
parser.add_argument('--num_file', type=int, required=True, help='Number of files to generate')
parser.add_argument('--sample_from', type=str, help='Optional .fasta file to sample from')
parser.add_argument('--kmer_length', type=int, default=1, help='Length of kmers to sample')
parser.add_argument('--seed', type=int, default=None, help='Optional seed for random number generator')
parser.add_argument('--output_dir', type=str, default='/mnt/data', help='Output directory for .fasta files')
parser.add_argument('--randomness', type=float, default=0.0, help='Amount of randomness to add to the kmer frequencies')
args = parser.parse_args()

# Set seed for random number generator
random.seed(args.seed)

# Define mean sequence length and standard deviation
mean_length = 10**6
std_dev = 10**5

# If a .fasta file is provided, calculate kmer frequencies from it
if args.sample_from:
    kmers, probabilities, counter = calculate_frequencies(args.sample_from, args.kmer_length)
    print(f'Sampled {args.kmer_length}-mer frequencies:')
    for kmer, freq in counter.items():
        print(f'{kmer}: {freq / sum(counter.values()):.4f}')
else:
    kmers, probabilities = ['A', 'C', 'G', 'T'], [0.25, 0.25, 0.25, 0.25]
    print('Nucleotide frequencies: A: 0.25, C: 0.25, G: 0.25, T: 0.25')

# Check if output directory exists
if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)
else:
    print(f'Warning: Output directory {args.output_dir} already exists. Existing files may be overwritten.')

# Loop over number of files
for i in range(1, args.num_file + 1):
    print(f'Generating file {i} of {args.num_file}')

    # Generate random sequence length
    seq_length = int(np.random.normal(mean_length, std_dev))

    # Add randomness to kmer frequencies
    new_probabilities = add_randomness(probabilities, args.randomness)

    # Generate random sequence
    sequence = ''.join(random.choices(kmers, weights=new_probabilities, k=seq_length // args.kmer_length))

    # Define fasta header
    header = f'>random_sequence_{i}'

    # Define file name
    filename = f'{args.output_dir}/{args.seed if args.seed else "random"}_random_sequence_{i}_{"sampled" if args.sample_from else "default"}_{args.kmer_length}mer.fasta'

    # Write sequence to file
    with open(filename, 'w') as f:
        f.write(header + '\n')
        f.write(sequence)

print('Finished generating .FASTA files.')
