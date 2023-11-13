import subprocess
import tempfile
import os
import shutil
import gzip
import requests
import re
from ftplib import FTP


# Global output directory for all genomes
output_dir = "genome_downloads"
os.makedirs(output_dir, exist_ok=True)

def download_patric_genomes(patric_ids):
    ftp_server = "ftp.patricbrc.org"
    ftp_path = "/genomes/"
    
    # Use the same output directory as for NCBI and ENA genomes
    os.makedirs(output_dir, exist_ok=True)

    for patric_id in patric_ids:
        file_name = f"{patric_id}.fna"
        local_file_path = os.path.join(output_dir, file_name)
        remote_file_path = f"{ftp_path}{patric_id}/{file_name}"

        print(f"Downloading: {patric_id}")

        with FTP(ftp_server) as ftp:
            ftp.login()  # anonymous login
            with open(local_file_path, 'wb') as local_file:
                try:
                    ftp.retrbinary(f"RETR {remote_file_path}", local_file.write)
                except Exception as e:
                    print(f"Error downloading {patric_id}: {e}")
                    if os.path.exists(local_file_path):
                        os.remove(local_file_path)

    # Calculate and print the download summary
    successful_downloads = [id for id in patric_ids if os.path.exists(os.path.join(output_dir, f"{id}.fna"))]
    downloaded_percentage = (len(successful_downloads) / len(patric_ids)) * 100 if patric_ids else 0
    print(f"Downloaded {downloaded_percentage:.2f}% of the expected PATRIC genomes.")

def is_patric_id(genome_id):
    # PATRIC IDs are typically numeric with a period and another number
    return re.match(r'^\d+\.\d+$', genome_id)

def reformat_and_download_genome_ids(input_file):
    with open(input_file, 'r') as file:
        genome_ids = file.read().splitlines()

    processed_ids = set()
    ncbi_ids = set()
    ena_ids = set()
    patric_ids = set()
    for genome_id in genome_ids:
        genome_id = genome_id.strip().strip('"')
        if genome_id == "NA" or not genome_id:
            continue
        if genome_id.startswith('GCA') and not '.' in genome_id:
            genome_id += '.1'
            ncbi_ids.add(genome_id)
        elif re.match(r'^[A-Z]{2}\d+', genome_id) and not genome_id.startswith('GCA'):
            ena_ids.add(genome_id)
        elif is_patric_id(genome_id):
            patric_ids.add(genome_id)
        processed_ids.add(genome_id)

    total_genomes = len(processed_ids)
    ncbi_genomes = len(ncbi_ids)
    ena_genomes = len(ena_ids)
    patric_genomes = len(patric_ids)
    print(f"Found {total_genomes} genome identifiers in the list.")
    print(f"Identified {ncbi_genomes} NCBI genome identifiers for download.")
    print(f"Identified {ena_genomes} ENA genome identifiers for download.")
    print(f"Identified {patric_genomes} PATRIC genome identifiers for download.")

    if ncbi_ids:
        download_ncbi_genomes(ncbi_ids, processed_ids)

    if ena_ids:
        reformat_and_download_ena_genome_ids(ena_ids)

    if patric_ids:
        download_patric_genomes(patric_ids)


def download_ncbi_genomes(ncbi_ids, processed_ids):
    temp_dir = tempfile.mkdtemp(prefix="ncbi_downloads_")
    temp_file = tempfile.NamedTemporaryFile(mode='w+', dir=temp_dir, delete=False)
    temp_file_path = temp_file.name
    # Create a temporary directory for the downloads
    print(f"Temporary download directory: {temp_dir}")

    # Write the IDs to a temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w+', dir=temp_dir, delete=False)
    temp_file_path = temp_file.name
    print(f"The NCBI accession list is saved at: {temp_file_path}")
    with temp_file as file:
        for id in ncbi_ids:
            file.write(id + '\n')

    # Construct the bash command
    cmd = [
        'ncbi-genome-download',
        '--assembly-accessions', temp_file_path,
        '--section', 'genbank',
        '--parallel', '5',
        '--no-cache',        
        '--output-folder', temp_dir,
        '--flat-output',
        '--retries', '10',
        '--formats', 'fasta',
        '--verbose', 'all'
    ]

    # Execute the download command
    print(f"Starting the download of {len(ncbi_ids)} NCBI genomes...")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Check the results of the download
    if result.returncode == 0:
        print("Finished download successfully.")
    else:
        print(f"Download failed with error: {result.stderr}")

    # Unpack and rename the files
    unpack_and_rename(temp_dir, processed_ids, ncbi_ids)

    # Move files to the output directory
    move_files_to_output_dir(temp_dir, output_dir)

    # Optionally, remove the temp directory
    shutil.rmtree(temp_dir)

    # Cleanup: remove the temporary file
    #os.remove(temp_file_path)
    # Optionally, you could also remove the temp directory if you want everything cleaned up
    # shutil.rmtree(temp_dir)

def unpack_and_rename(download_dir, processed_ids, ncbi_ids):
    downloaded_files = []
    for file_name in os.listdir(download_dir):
        if file_name.endswith('.gz'):
            # Extract the base name without the version and additional text
            base_name = file_name.split('_genomic.fna.gz')[0]
            stripped_base_name = '.'.join(base_name.split('.')[:-1])  # Remove version

            # Construct the full paths
            gz_file_path = os.path.join(download_dir, file_name)
            fasta_file_path = os.path.join(download_dir, stripped_base_name + '.fasta')

            # Unzip the file
            with gzip.open(gz_file_path, 'rb') as f_in:
                with open(fasta_file_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Check if the file is empty
            if os.path.getsize(fasta_file_path) == 0:
                print(f"Warning: {fasta_file_path} is empty. Removing file.")
                os.remove(fasta_file_path)
            else:
                downloaded_files.append(stripped_base_name)

            # Remove the original .gz file
            os.remove(gz_file_path)

    # Compare downloaded files with the expected list
    compare_downloaded_with_expected(downloaded_files, ncbi_ids, download_dir)

def move_files_to_output_dir(temp_dir, output_dir):
    for file_name in os.listdir(temp_dir):
        source_file = os.path.join(temp_dir, file_name)
        if os.path.isfile(source_file) and file_name.endswith('.fasta'):
            shutil.move(source_file, os.path.join(output_dir, file_name))

def compare_downloaded_with_expected(downloaded_files, ncbi_ids, download_dir):
    # Only consider NCBI IDs for comparison
    expected_ncbi_ids = ncbi_ids

    # Convert downloaded_files to NCBI format for comparison
    downloaded_ncbi_ids = set(f"{id}.1" for id in downloaded_files if id.startswith('GCA'))

    downloaded_percentage = (len(downloaded_ncbi_ids) / len(expected_ncbi_ids)) * 100 if expected_ncbi_ids else 0
    missing_ids = expected_ncbi_ids - downloaded_ncbi_ids

    # Write the reports to files
    with open('ncbi_genome_download_report.txt', 'w') as report_file, \
         open('ncbi_genome_download_report_failed.txt', 'w') as failed_file:
        if missing_ids:
            for missing_id in missing_ids:
                failed_file.write(missing_id + '\n')
            print(f"NCBI genome download report for missing/empty genomes is available in 'ncbi_genome_download_report_failed.txt'")
        for downloaded_id in downloaded_ncbi_ids:
            report_file.write(downloaded_id + '\n')


def reformat_and_download_ena_genome_ids(ena_ids):
    # No need to read from a file, as we already have the ENA IDs in a set
    total_genomes = len(ena_ids)
    print(f"Found {total_genomes} ENA genome identifiers for download.")

    # Download genomes from ENA
    if ena_ids:
        download_ena_genomes(ena_ids)

def download_ena_genomes(genome_ids):
    print(f"Downloading ENA genomes to: {output_dir}")

    downloaded_files = []
    failed_downloads = []
    
    # URL components
    url_prefix = "https://www.ebi.ac.uk/ena/browser/api/fasta/"
    url_suffix = "?download=true"

    for ena_id in genome_ids:
        # Construct the URL
        url = f"{url_prefix}{ena_id}{url_suffix}"
        
        # File path in the output directory
        file_path = os.path.join(output_dir, f"{ena_id}.fasta")
        
        # Download the file
        print(f"Downloading: {ena_id}")
        response = requests.get(url)
        
        # Check if the download was successful (response code 200)
        if response.status_code == 200:
            with open(file_path, 'wb') as file:
                file.write(response.content)
            # Check if the file is empty
            if os.path.getsize(file_path) > 0:
                downloaded_files.append(ena_id)
            else:
                print(f"Warning: File {file_path} is empty")
                failed_downloads.append(ena_id)
                os.remove(file_path)
        else:
            print(f"Failed to download {ena_id}")
            failed_downloads.append(ena_id)

    generate_reports_ena(downloaded_files, failed_downloads, genome_ids)

def generate_reports_ena(downloaded_files, failed_downloads, ena_ids):
    downloaded_percentage = (len(downloaded_files) / len(ena_ids)) * 100 if ena_ids else 0
    missing_ids = ena_ids - set(downloaded_files)

    with open('ena_genome_download_report.txt', 'w') as report_file, \
         open('ena_genome_download_report_failed.txt', 'w') as failed_file:
        for downloaded_id in downloaded_files:
            report_file.write(downloaded_id + '\n')
        for failed_id in missing_ids:
            failed_file.write(failed_id + '\n')
        print(f"Downloaded {downloaded_percentage:.2f}% of the expected ENA genomes.")
        if missing_ids:
            print(f"ENA genome download report for missing/empty genomes is available in 'ena_genome_download_report_failed.txt'")
