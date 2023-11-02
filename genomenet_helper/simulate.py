import os
import random
import collections
import numpy as np
from Bio import SeqIO
from .utils import generate_output_directory

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

def simulate_genomes(input_dir, sim_size_kb=100, kmer_length=3, seed=None, randomness=0.0):
    num_file = 1  # Assuming you're simulating one genome sequence per input fasta file.
    
    output_dir = generate_output_directory(input_dir, "simulated")

    for fasta_file in os.listdir(input_dir):
        if fasta_file.endswith('.fasta'):
            input_path = os.path.join(input_dir, fasta_file)
            
            random.seed(seed)

            mean_length = sim_size_kb * 1000  # Convert kb to bases
            std_dev = 10**5

            kmers, probabilities, counter = calculate_frequencies(input_path, kmer_length)
            
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            seq_length = int(np.random.normal(mean_length, std_dev))
            new_probabilities = add_randomness(probabilities, randomness)
            
            sequence = ''.join(random.choices(kmers, weights=new_probabilities, k=seq_length // kmer_length))
            
            header = f'>random_sequence_{num_file}'
            filename = f'{output_dir}/{seed if seed else "random"}_random_sequence_{num_file}_sampled_{kmer_length}mer.fasta'

            with open(filename, 'w') as f:
                f.write(header + '\n')
                f.write(sequence)

            num_file += 1

    print(f'Finished generating simulated genomes in {output_dir}.')
