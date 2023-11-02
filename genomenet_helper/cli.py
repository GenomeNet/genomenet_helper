import argparse
from .subsample import subsample_genomes
from .simulate import simulate_genomes
from .split import split_files

def main():
    parser = argparse.ArgumentParser(description='GenomeNet Helper')
    subparsers = parser.add_subparsers(dest='command')

    # Subsample command
    parser_subsample = subparsers.add_parser('subsample')
    parser_subsample.add_argument('--input', type=str, required=True)
    parser_subsample.add_argument('--fragment_length', type=int, default=4000)
    parser_subsample.add_argument('--n_fragments', type=int, default=2500)

    # Simulate command
    parser_simulate = subparsers.add_parser('simulate')
    parser_simulate.add_argument('--input', type=str, required=True)
    parser_simulate.add_argument('--sim_size_kb', type=int, default=100)

   # Split command
    parser_split = subparsers.add_parser('split')
    parser_split.add_argument('--input', type=str, required=True)
    parser_split.add_argument('--fraction', type=int, nargs=3, required=True, 
                              help="Fractions for train, validation, and test datasets respectively (must sum up to 100)")
    parser_split.add_argument('--by-size', action='store_true', 
                              help="Split files based on size rather than count")


    args = parser.parse_args()

    if args.command == 'subsample':
        subsample_genomes(args.input, args.fragment_length, args.n_fragments)
    elif args.command == 'simulate':
        simulate_genomes(args.input, args.sim_size_kb)
    if args.command == "subsample":
        subsample_genomes(args.input, args.fragment_length, args.n_fragments)
    elif args.command == 'split':
        split_files(args.input, args.fraction, args.by_size)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()