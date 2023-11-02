# GenomeNet Helper

GenomeNet Helper is a tool designed to assist in the downloading and processing of genome files for deep learning model training. The application provides functionalities to subsample and simulate genome sequences based on user input.

## Features

- **Subsampling**: Generate subsamples from genome fasta files based on specified fragment length and number.
- **Simulation**: Simulate genome sequences either from provided k-mer frequencies of a fasta file or using default nucleotide frequencies.

## Usage

### Subsampling

To subsample genome files:

```
genomenet_helper subsample --input [input_dir] [--fragment_length 4000] [--n_fragments 2500]
```

- `input_dir`: Directory containing input fasta files.
- `fragment_length`: (Optional) Length of each fragment. Default is `4000`.
- `n_fragments`: (Optional) Number of fragments to sample. Default is `2500`.

Output directory is generated automatically based on input directory name and date, in the format `$inputname_subsampled_date`.

### Simulation

To simulate genome sequences:

```
genomenet_helper simulate --input [input_dir] [--sim_size_kb 100] [--kmer_length 3] [--randomness 0.0] [--seed [random_seed_number]]
```

- `input_dir`: Directory containing input fasta files.
- `sim_size_kb`: (Optional) Size of the simulated file in kilobases. Default is `100`.
- `kmer_length`: (Optional) Length of kmers to consider. Default is `3`.
- `randomness`: (Optional) Amount of randomness to add to the kmer frequencies. Default is `0.0`.
- `seed`: (Optional) Seed for random number generation.
