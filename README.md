# GenomeNet Helper

GenomeNet Helper is a tool designed to assist in the downloading and processing of genome files for deep learning model training. The application provides functionalities to subsample and simulate genome sequences based on user input.

## Features
- **Genome download**: Download genomes based on a list of genome IDS from NCBI, ENA and PATRIC
- **Splitting**: Splitting the dataset up to train/test/validation by file size.
- **Subsampling**: Generate subsamples from genome fasta files based on specified fragment length and number.
- **Simulation**: Simulate genome sequences either from provided k-mer frequencies of a fasta file or using default nucleotide frequencies.
- **Merging**: Merge the Subsampling/Simulation output to generate final train/test/validaion folders
- **Uploading**: Upload to B2

TODO:
- add baseline classifiers (alignment based / k-mer based)
- query from BacDive table
- calculate genome quality scores

## Installation

Before installing the package, it's a good idea to set up a virtual environment to avoid potential conflicts with other Python packages.

```
virtualenv venv
source venv/bin/activate
```

You'll need to clone the repository to your local machine. Navigate to the directory where you want the project to live and run the following command:

```
git clone https://github.com/GenomeNet/genomenet_helper.git
cd genomenet_helper
pip install .
```

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

### Splitting

To split genome files into train, validation, and test sets:

```
genomenet_helper split --input [input_dir] [--fractions 80,10,10] [--by_size False]
```

- `input_dir`:  Directory containing input fasta files.
- `fractions`: (Optional) Percentages to split the data into train, validation, and test sets respectively. Default is 80,10,10.
- `by_size`: (Optional) If set to True, the files will be split based on their size in bytes, ensuring that the output directories adhere closely to the specified fractions in terms of total size. If set to False, the files will be randomly split by count. Default is False.

Output directories for train, validation, and test sets are generated automatically based on input directory name, in the format $inputname_train_date, $inputname_validation_date, and $inputname_test_date respectively.
