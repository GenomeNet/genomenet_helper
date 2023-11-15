import argparse
from .subsample import subsample_genomes
from .simulate import simulate_genomes
from .split import split_files
from .upload import upload_dataset
from .merge import merge_datasets
from .genome_downloader import reformat_and_download_genome_ids
from .kmer_profiling import process_kmer_profiles
from .model_trainer import process_model_training
from .kmer_harmonization import harmonize_kmer_headers

def main():
    parser = argparse.ArgumentParser(description='GenomeNet Helper')
    subparsers = parser.add_subparsers(dest='command')

    # Shared input argument definition for multiple directories (used for subsample, simulate, and clean)
    multi_input_argument = argparse.ArgumentParser(add_help=False)
    multi_input_argument.add_argument('--input', type=str, nargs='+', required=True, help='One or more input directories to process')

    # Specific input argument definition for a single directory (used for split)
    split_input_argument = argparse.ArgumentParser(add_help=False)
    split_input_argument.add_argument('--input', type=str, required=True, help='Input directory to process')

    # Subsample command
    parser_subsample = subparsers.add_parser('subsample', parents=[multi_input_argument])
    parser_subsample.add_argument('--fragment_length', type=int, default=4000)
    parser_subsample.add_argument('--n_fragments', type=int, default=2500)

    # Simulate command
    parser_simulate = subparsers.add_parser('simulate', parents=[multi_input_argument])
    parser_simulate.add_argument('--sim_size_kb', type=int, default=100)

    # Split command
    parser_split = subparsers.add_parser('split', parents=[split_input_argument])
    parser_split.add_argument('--fraction', type=float, nargs=3, required=True,
                            help="Fractions for train, validation, and test datasets respectively (must sum up to 100)")
    parser_split.add_argument('--by-size', action='store_true',
                            help="Split files based on size rather than count")

    # Upload command
    parser_upload = subparsers.add_parser('upload')
    parser_upload.add_argument('--train', type=str, required=True, help="Path to the training data folder")
    parser_upload.add_argument('--test', type=str, required=True, help="Path to the test data folder")
    parser_upload.add_argument('--validation', type=str, required=True, help="Path to the validation data folder")

    # Merge command
    parser_merge = subparsers.add_parser('merge')
    parser_merge.add_argument('--input', type=str, required=True, help='The base name for input directories.')
    parser_merge.add_argument('--date', type=str, required=True, help='The date suffix for the directories.')

    # Add a new subparser for the genome_download command
    parser_genome_download = subparsers.add_parser('genome_download')
    parser_genome_download.add_argument('--input', type=str, required=True, help='Path to the file containing the list of genome IDs.')

     # K-mer profiling command
    parser_kmer = subparsers.add_parser('kmer')
    parser_kmer.add_argument('--input', type=str, required=True, help='Input directory containing fasta files')
    parser_kmer.add_argument('--kmer_size', type=int, default=7, help='Size of k-mers')
    parser_kmer.add_argument('--max_subseqs', type=int, default=20, help='Maximum number of subsequences to process from each fasta file')
    parser_kmer.add_argument('--subsequence_size', type=int, default=2000, help='Size of each subsequence to be processed')
    parser_kmer.add_argument('--random_mode', action='store_true', help='Enable random mode to randomly select subsequences')
    parser_kmer.add_argument('--label', type=str, default="", help='Label for the output data')

    # K-mer Harmonize command
    parser_kmer_harmonize = subparsers.add_parser('kmer-harmonize')
    parser_kmer_harmonize.add_argument('files', nargs='+', help='Paths to the CSV files to harmonize')

    # Add a new subparser for the model training command
    parser_model_train = subparsers.add_parser('train_model')
    parser_model_train.add_argument('--input_train', type=str, nargs='+', required=True, help='CSV files for training')
    parser_model_train.add_argument('--input_test', type=str, nargs='+', required=True, help='CSV files for testing')
    parser_model_train.add_argument('--output', type=str, default="combined_report.pdf", help='Output path for the report')

    args = parser.parse_args()
    if args.command == 'subsample':
        for input_dir in args.input:
            subsample_genomes(input_dir, args.fragment_length, args.n_fragments)
    elif args.command == 'simulate':
        for input_dir in args.input:
            simulate_genomes(input_dir, args.sim_size_kb, monitor_kmers=["ATG", "TTT", "GCA", "CGT", "AAC"])
    elif args.command == 'split':
        split_files(args.input, args.fraction, args.by_size)
    elif args.command == 'upload':
        upload_dataset(args.train, args.test, args.validation)
    elif args.command == 'merge':
        merge_datasets(args.input, args.date)
    elif args.command == 'kmer':
        process_kmer_profiles(args.input, args.kmer_size, args.max_subseqs, args.subsequence_size, args.random_mode, args.label)
    elif args.command == 'train_model':
        process_model_training(args.input_train, args.input_test, args.output)
    elif args.command == 'kmer-harmonize':
        harmonize_kmer_headers(*args.files)
    elif args.command == 'genome_download':
        reformat_and_download_genome_ids(args.input)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
