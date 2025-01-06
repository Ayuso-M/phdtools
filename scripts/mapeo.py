import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mne
from matplotlib.animation import FuncAnimation

# Define frequency bands
BANDS = {
    'Delta': [0.5, 4],
    'Theta': [4, 8],
    'Alpha': [8, 12],
    'Beta': [12, 30],
    'Gamma': [30, 50]
}

# Function to load EEG data from CSV files
def load_csv_files(folder_path, file_list, electrodes):
    """
    Load EEG data from CSV files.

    Parameters:
    - folder_path (str): Path to the folder containing the CSV files.
    - file_list (list): List of CSV file names to load.
    - electrodes (list): List of electrode names.

    Returns:
    - dict: Dictionary containing EEG data for each file.
    """
    data = {}
    for file_name in file_list:
        file_path = os.path.join(folder_path, file_name)
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
        try:
            eeg_data = pd.read_csv(file_path, index_col=0)  # Use the first column as the index
            if 'ECG_artificial' in eeg_data.index:
                eeg_data = eeg_data.drop('ECG_artificial', axis=0)
            if len(eeg_data) != len(electrodes):
                print(f"Mismatch in electrode count for file: {file_name}")
                continue
            data[file_name] = eeg_data
            print(f"File loaded: {file_name}")
        except Exception as e:
            print(f"Error loading file {file_name}: {e}")
    return data

# Function to create EEG info structure
def create_eeg_info(electrodes, sfreq=256):
    """
    Create MNE Info object with a standard 10-20 montage.

    Parameters:
    - electrodes (list): List of electrode names.
    - sfreq (float): Sampling frequency (default is 256 Hz).

    Returns:
    - mne.Info: EEG Info object.
    """
    info = mne.create_info(ch_names=electrodes, sfreq=sfreq, ch_types='eeg')
    montage = mne.channels.make_standard_montage('standard_1020')
    info.set_montage(montage)
    return info

# Function to compute average power in frequency bands
def compute_band_powers(raw, bands):
    """
    Compute the average power for each frequency band.

    Parameters:
    - raw (mne.io.Raw): Preprocessed EEG data.
    - bands (dict): Dictionary of frequency bands.

    Returns:
    - dict: Band powers for each frequency band.
    """
    psds = raw.compute_psd(fmin=0.5, fmax=50, n_fft=2048)
    freqs = psds.freqs
    psd_data = psds.get_data()

    band_powers = {}
    for band, (fmin, fmax) in bands.items():
        idx_band = np.logical_and(freqs >= fmin, freqs <= fmax)
        band_power = np.mean(psd_data[:, idx_band], axis=1)
        band_powers[band] = band_power
    return band_powers

# Function to generate topographic maps
def plot_topomaps(band_powers, info, output_folder, prefix=""):
    """
    Generate topographic maps for each frequency band.

    Parameters:
    - band_powers (dict): Band powers for each frequency band.
    - info (mne.Info): EEG Info object.
    - output_folder (str): Folder to save the images.
    - prefix (str): Prefix for image file names.
    """
    for band, power in band_powers.items():
        fig, ax = plt.subplots(figsize=(6, 6))
        mne.viz.plot_topomap(
            power, info, axes=ax, show=False, cmap='viridis', 
            sphere=(0.00, 0.0, 0.0, 0.09)  # Adjust head size
        )
        ax.set_title(f"{band} band")
        image_path = os.path.join(output_folder, f"{prefix}_{band}.png")
        plt.tight_layout()
        plt.savefig(image_path, dpi=300)
        plt.close()
        print(f"Saved topomap: {image_path}")

# Function to create EEG activation animation
def create_activation_animation(raw, output_file):
    """
    Create an EEG activation animation over time.

    Parameters:
    - raw (mne.io.Raw): Preprocessed EEG data.
    - output_file (str): Path to save the animation (GIF or MP4).
    """
    times = np.arange(0, len(raw.times), 1000)  # Adjust step size for time
    fig, ax = plt.subplots()

    def update_topomap(frame):
        ax.clear()
        time = raw.times[frame]
        data = raw.copy().crop(tmin=time, tmax=time + 1/raw.info['sfreq']).get_data()
        mne.viz.plot_topomap(data[:, 0], raw.info, axes=ax, show=False, cmap='viridis')
        ax.set_title(f'Time: {time:.2f} s')

    anim = FuncAnimation(fig, update_topomap, frames=times, interval=200, repeat=False)
    anim.save(output_file, writer='imagemagick', fps=10)
    plt.show()
    print(f"Animation saved: {output_file}")

# Main execution
if __name__ == "__main__":
    # Paths and parameters
    data_folder = "/path/to/your/csv/files"
    output_folder = "/path/to/save/images"
    file_list = [f"P_OApre_psd_bands_{i}_emotiv.csv" for i in range(1, 13)]
    electrodes = ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 
                  'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4']

    # Load data
    eeg_data = load_csv_files(data_folder, file_list, electrodes)

    # Create EEG info
    info = create_eeg_info(electrodes)

    # Process each file
    for file_name, data in eeg_data.items():
        # Create RawArray for processing
        raw = mne.io.RawArray(data.values.T, info)

        # Compute band powers
        band_powers = compute_band_powers(raw, BANDS)

        # Generate topomaps
        plot_topomaps(band_powers, info, output_folder, prefix=file_name)

        # Create animation (optional)
        animation_file = os.path.join(output_folder, f"{file_name}_animation.gif")
        create_activation_animation(raw, animation_file)
