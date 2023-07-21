import os
import random 
import argparse
from subsample_genomes import sample_fasta_files
from create_sim import calculate_frequencies, add_randomness
from create_sim import simulate_genome


def create_simulated_fasta(input_file, output_dir, sequence_length, kmer_length=3, randomness=0.0, seed=None):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    kmers, probabilities, _ = calculate_frequencies(input_file, kmer_length)
    new_probabilities = add_randomness(probabilities, randomness)

    sequence = ''.join(random.choices(kmers, weights=new_probabilities, k=sequence_length // kmer_length))

    header = f'>random_sequence_simulated'
    filename = os.path.join(output_dir, os.path.basename(input_file).replace('.fasta', '_sim.fasta'))

    with open(filename, 'w') as f:
        f.write(header + '\n')
        f.write(sequence)

    print(f'Successfully generated simulated file, written to {filename}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process fasta files.')
    parser.add_argument('--input_dir', type=str, required=True, help='Directory containing input fasta files')
    parser.add_argument('--output_dir', type=str, required=True, help='Directory to save output fasta files')
    parser.add_argument('--fragment_length', type=int, default=10000, help='Length of each fragment')
    parser.add_argument('--n_fragments', type=int, default=10, help='Number of fragments to sample')
    parser.add_argument('--sequence_length', type=int, default=10**6, help='Length of the simulated sequence')
    parser.add_argument('--kmer_length', type=int, default=3, help='Length of kmers to sample')
    parser.add_argument('--randomness', type=float, default=0.0, help='Amount of randomness to add to the kmer frequencies')
    parser.add_argument('--seed', type=int, default=None, help='Optional seed for random number generator')
    args = parser.parse_args()

    sample_fasta_files(args.input_dir, args.output_dir, args.fragment_length, args.n_fragments)

    for file in os.listdir(args.output_dir):
        if file.endswith('.fasta'):
            input_file = os.path.join(args.output_dir, file)
            create_simulated_fasta(input_file, args.output_dir, args.sequence_length, args.kmer_length, args.randomness, args.seed)

