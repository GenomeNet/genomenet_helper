import argparse
from Bio import Entrez

def get_tax_info(taxid):
    Entrez.email = 'mail@pmuench.com'  # Always tell NCBI who you are
    handle = Entrez.efetch(db="Taxonomy", id=str(taxid), retmode="xml")
    records = Entrez.read(handle)
    name = records[0]['ScientificName']
    lineage = records[0]['Lineage']
    return name, lineage

def main(input_file):
    with open(input_file, 'r') as file:
        taxids = [int(line.strip()) for line in file]
    for taxid in taxids:
        name, lineage = get_tax_info(taxid)
        print(f'TaxID: {taxid}, Name: {name}, Lineage: {lineage}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Annotate TaxIDs with their names and lineage.')
    parser.add_argument('--input', type=str, required=True, help='Input file with a list of TaxIDs')
    args = parser.parse_args()
    main(args.input)

