import os
import re
import mne
import numpy as np
import pandas as pd
from scipy.signal import welch  # Usar scipy para calcular la PSD

# Define frequency bands
bands = {
    'Delta': [0.5, 4],
    'Theta': [4, 8],
    'Alpha': [8, 12],
    'Beta': [12, 30],
    'Gamma': [30, 50]
}

# Function to extract metadata (subject, condition, measurement) from file name
def extract_metadata(file_name):
    """
    Extract measurement, condition, and subject metadata from the file name.
    Expected format: M1_CONDITION_SUBJECT...
    """
    measure_match = re.search(r'M\d+', file_name)
    measurement = measure_match.group() if measure_match else "Unknown"

    condition_match = re.search(r'M\d+_(\w+)', file_name)
    condition = condition_match.group(1) if condition_match else "Unknown"

    subject_match = re.search(r'F\d{3}', file_name)
    subject = subject_match.group() if subject_match else "Unknown"

    return measurement, condition, subject

# Function to calculate power for each frequency band
def calculate_band_power(raw_clean):
    """
    Calculate the average power for each frequency band across all channels.
    """
    # Extract data from the preprocessed file
    data = raw_clean.get_data()  # Shape: channels × timepoints
    sfreq = raw_clean.info['sfreq']  # Sampling frequency

    # Calculate Welch's PSD using scipy
    freqs, psds = welch(data, fs=sfreq, nperseg=1024, axis=1)

    # Convert power to decibels
    psds_db = 10 * np.log10(psds)

    # Create a dictionary to store results
    band_results = {}
    for band, (fmin, fmax) in bands.items():
        idx_band = np.logical_and(freqs >= fmin, freqs <= fmax)
        band_power = psds_db[:, idx_band].mean(axis=1)  # Mean power for each channel in the band
        band_results[f'{band}_mean'] = band_power.mean()  # Global average
        for idx, ch_name in enumerate(raw_clean.info['ch_names']):
            band_results[f'{band}_{ch_name}'] = band_power[idx]  # Power per channel
    return band_results

# Function to process `.fif` files and generate the results table
def process_fif_files(input_folder, output_csv):
    """
    Process preprocessed `.fif` files and generate a CSV with power band data.
    """
    fif_files = [file for file in os.listdir(input_folder) if file.endswith('.fif')]
    if not fif_files:
        print("No `.fif` files found in the specified folder.")
        return

    all_results = []
    for file in fif_files:
        print(f"Processing file: {file}")
        file_path = os.path.join(input_folder, file)

        # Extract metadata
        measurement, condition, subject = extract_metadata(file)

        # Load the preprocessed data
        try:
            raw_clean = mne.io.read_raw_fif(file_path, preload=True)
        except Exception as e:
            print(f"Error loading file {file}: {e}")
            continue

        # Calculate power for each band
        file_results = {'file': file, 'measurement': measurement, 'condition': condition, 'subject': subject}
        try:
            band_powers = calculate_band_power(raw_clean)
            file_results.update(band_powers)
        except Exception as e:
            print(f"Error calculating power for file {file}: {e}")
            continue

        # Add results to the list
        all_results.append(file_results)

    # Convert results to a DataFrame
    if all_results:
        df_results = pd.DataFrame(all_results)
        df_results.to_csv(output_csv, index=False)
        print(f"Results saved to: {output_csv}")
    else:
        print("No results were generated due to errors.")

# Main Execution
if __name__ == "__main__":
    # Folder containing preprocessed `.fif` files
    input_folder = "/Users/rosaayusomoreno/Desktop/phdtools/data_eeg/filtered_data"
    output_csv = "/Users/rosaayusomoreno/Desktop/phdtools/data_eeg/filtered_data/results_power_bands.csv"

    # Process files and generate the results table
    process_fif_files(input_folder, output_csv)
