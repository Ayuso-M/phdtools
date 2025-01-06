import os
import mne
from pyprep.prep_pipeline import PrepPipeline
from scipy.signal import welch
import numpy as np
import matplotlib.pyplot as plt

# Function to load EDF files from a folder
def load_edf_files(folder_path, keyword=None):
    """
    Generator to load EDF files from a folder iteratively.

    Parameters:
    - folder_path (str): Path to the folder containing the EDF files.
    - keyword (str, optional): If specified, only files containing this keyword in their name will be loaded.

    Yields:
    - raw (mne.io.Raw): MNE Raw object for the loaded EDF file.
    - file_name (str): Name of the EDF file being loaded.
    """
    edf_files = [
        os.path.join(folder_path, file)
        for file in os.listdir(folder_path)
        if file.endswith(".edf") and (keyword in file if keyword else True)
    ]

    print(f"Found {len(edf_files)} EDF files.")

    for idx, file_path in enumerate(edf_files, start=1):
        print(f"[{idx}/{len(edf_files)}] Loading file: {file_path}")
        raw = mne.io.read_raw_edf(file_path, preload=True)  # Load into memory
        yield raw, file_path

# Function to preprocess a single raw file
def preprocess_raw(raw):
    """
    Preprocess an MNE Raw object.
    Steps:
        1. Resample to 128 Hz.
        2. Bandpass filter (1-50 Hz).
        3. Apply montage (10-20 system).
        4. Run PyPREP for bad channel detection/interpolation.
        5. Re-reference to the average.
        6. Perform ICA for artifact removal.
        7. Compute Welch's PSD.

    Returns:
        dict: Preprocessed data and PSD results.
    """
    # 1. Resample
    raw.resample(sfreq=128)
    print(f"Resampled to {raw.info['sfreq']} Hz")

    # 2. Bandpass filter
    raw.filter(l_freq=1, h_freq=50)
    print("Applied bandpass filter: 1-50 Hz")

    # 3. Apply montage
    ch_names = ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4']
    raw.pick_channels(ch_names)
    montage = mne.channels.make_standard_montage('standard_1020')
    raw.set_montage(montage)
    print("Montage applied")

    # 4. Run PyPREP
    prep_params = {
        "ref_chs": "eeg",
        "reref_chs": "eeg",
        "line_freqs": np.arange(50, raw.info['sfreq'] / 2, 50),
        "max_iterations": 8,
    }
    prep_pipeline = PrepPipeline(raw, prep_params, raw.get_montage())
    prep_pipeline.fit()

    print("Bad channels interpolated:", prep_pipeline.interpolated_channels)
    print("Original bad channels:", prep_pipeline.noisy_channels_original["bad_all"])
    print("Bad channels after interpolation:", prep_pipeline.still_noisy_channels)

    raw = prep_pipeline.raw.copy()

    # 5. Re-reference to the average
    raw.set_eeg_reference('average', projection=True)
    print("Re-referenced to the average")

    # 6. ICA
    ica = mne.preprocessing.ICA(n_components=0.99, method='fastica', random_state=42)
    ica.fit(raw)
    ica.plot_components(inst=raw)  # Optional: Plot components for manual inspection
    ica.apply(raw)
    print("ICA applied and artifacts removed")

    # 7. Welch's PSD
    f, psd = welch(raw.get_data(), fs=raw.info['sfreq'], nperseg=1024)

    return {"cleaned_raw": raw, "frequencies": f, "psd": psd}

# Function to apply preprocessing to multiple files
def apply_to_files(folder_path, keyword=None):
    """
    Apply preprocessing to all EDF files in a folder.

    Parameters:
    - folder_path (str): Path to the folder containing EDF files.
    - keyword (str, optional): Filter files by keyword.

    Returns:
        dict: Results of preprocessing for each file.
    """
    results = {}
    for raw, file_path in load_edf_files(folder_path, keyword):
        print(f"Preprocessing file: {file_path}")
        result = preprocess_raw(raw)
        results[file_path] = result
    return results

# Function to plot Welch's PSD
def plot_psd(psd_data, freqs, title="Power Spectral Density"):
    """
    Plot the Power Spectral Density using Welch's method.

    Parameters:
    - psd_data (np.ndarray): PSD values.
    - freqs (np.ndarray): Corresponding frequencies.
    - title (str): Title for the plot.
    """
    plt.figure(figsize=(10, 6))
    plt.semilogy(freqs, np.mean(psd_data, axis=0))
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power Spectral Density (uV^2/Hz)')
    plt.title(title)
    plt.grid()
    plt.show()

# Main execution
if __name__ == "__main__":
    # Path to the folder with EDF files
    folder_path = "Cualsea"  # Change to your folder path
    keyword = "EPOC"  # Filter by keyword or set to None to load all files

    # Apply preprocessing to all files
    results = apply_to_files(folder_path, keyword)

    # Handle results
    for file_path, result in results.items():
        print(f"File: {file_path}")
        print(f"Frequencies: {result['frequencies']}")
        print(f"PSD Shape: {result['psd'].shape}")

        # Plot PSD for each file
        plot_psd(result['psd'], result['frequencies'], title=f"PSD for {os.path.basename(file_path)}")
