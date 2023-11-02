import os
from datetime import datetime

def generate_output_directory(input_dir, descriptor):
    """
    Given an input directory and a descriptor (e.g., "subsampled"), this function returns an output directory name.
    """
    current_date = datetime.today().strftime('%Y%m%d')
    base_name = os.path.basename(os.path.normpath(input_dir))
    
    # Removing the date from the base_name if present.
    if current_date in base_name:
        base_name = "_".join(base_name.split("_")[:-1])
        
    return os.path.join(os.path.dirname(input_dir), f"{base_name}_{descriptor}_{current_date}")
