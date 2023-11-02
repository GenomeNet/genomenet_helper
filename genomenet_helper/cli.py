import argparse
from .subsample import subsample_genomes
from .simulate import simulate_genomes
from .split import split_files
from .upload import upload_dataset
from .merge import merge_datasets

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
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
