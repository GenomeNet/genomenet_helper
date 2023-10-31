# simple_sequence_simulator
- Subsamples .fasta files in a folder
- Additionally generated simulated data with 3mer profile of each .fasta file

## Usage

```
python process.py --fragment_length 4000 --n_fragments 2500 --input_dir test --output_dir test_subsampled --sim_output_dir test_sim --sim_size_kb 100
```

### Output

```
Processing file 1/1
Successfully generated 1368 fragments, written to test_subsampled/Akkermansia_muciniphila.fasta
Successfully generated simulated file, written to test_sim/Akkermansia_muciniphila_sim.fasta
```
