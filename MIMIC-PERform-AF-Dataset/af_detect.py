import numpy as np
import neurokit2 as nk
import csv,os
from typing import List, Dict
from tqdm import tqdm
import warnings


AF_FOLDER = "AF-Subjects"
NON_AF_FOLDER = "Non-AF-Subjects"
SAMPLING_RATE:int = 125

def read_csv(file_path:str) -> List[Dict]:
    """Read CSV file and return list of dictionaries"""
    data = []
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def get_ppg_data(data:List[Dict]) -> List[float]:
    """Extract PPG data from the dataset"""
    ppg_data = []
    for row in data:
        ppg_data.append(float(row['PPG']))
    return ppg_data

def get_ipi_data(data: List[float]) -> np.ndarray:
    """Extract IPI data from the dataset and capture warnings"""
    try:
        # Capture warnings in a list
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")  # Trigger all warnings
            cleaned_ppg = nk.ppg_clean(data, sampling_rate=SAMPLING_RATE)
            
            # Print captured warnings
            if w:
                return np.array([])

        peaks = nk.ppg_peaks(cleaned_ppg, sampling_rate=SAMPLING_RATE)[1].get('PPG_Peaks')
        ibi = np.diff(peaks) / SAMPLING_RATE * 1000
        return np.array(ibi)

    except Exception as e:
        print(f"Error in get_ipi_data: {e}")
        return np.array([])

def rmssd(ibi):
    """Compute RMSSD of an IBI series"""
    ibi_diff = np.diff(ibi)
    return np.sqrt(np.mean(ibi_diff**2))

def normalized_rmssd(ibi):
    """Compute normalized RMSSD (RMSSD / mean IBI)"""
    return rmssd(ibi) / np.mean(ibi)

def coefficient_of_variation(ibi):
    """Compute CV of IBI series"""
    return np.std(ibi) / np.mean(ibi)

def pnnx(ibi, x=50):
    """
    Compute pNNx: percentage of successive intervals differing by more than x ms
    Default x=50 ms for AF detection
    """
    ibi_diff = np.abs(np.diff(ibi))
    return 100 * np.sum(ibi_diff > x) / len(ibi_diff)

def detect_af(ibi, rmssd_thresh=0.1, cv_thresh=0.1, pnnx_thresh=20, pnnx_x=50):
    """
    Detect AF based on thresholds for normalized RMSSD, CV, and pNNx.
    Returns True if AF suspected, False otherwise
    """
    nrmssd = normalized_rmssd(ibi)
    cv = coefficient_of_variation(ibi)
    pnnx_val = pnnx(ibi, x=pnnx_x)
    
    af_flags = {
        "normalized_rmssd": nrmssd > rmssd_thresh,
        "cv": cv > cv_thresh,
        f"pnn{pnnx_x}": pnnx_val > pnnx_thresh
    }
    # print(f"nRMSSD: {nrmssd:.4f}, CV: {cv:.4f}, pNN{pnnx_x}: {pnnx_val:.2f}, Flags: {af_flags}")
    af_detected = all(af_flags.values())
    
    return af_detected, af_flags

if __name__ == "__main__":
    file = open("labels.csv",'w')
    writer = csv.DictWriter(file, fieldnames=["file_name", "detected_time_segment", "af_detected", "normalized_rmssd", "cv", "pnn50"])
    writer.writeheader()

    csv_files = [f for f in os.listdir(AF_FOLDER) if f.endswith('.csv')]
    csv_files.sort()
    segment_length = SAMPLING_RATE * 30 
    overlapping_length = SAMPLING_RATE * 5

    for csv_file in tqdm(csv_files, desc="Processing CSV files"):
        csv_data = read_csv(os.path.join(AF_FOLDER, csv_file))
        ppg_data = get_ppg_data(csv_data)
        af_detected_ = False
        for start in range(0, len(ppg_data) - segment_length, overlapping_length):
            segment_ppg = ppg_data[start:start + segment_length]
            if len(segment_ppg) < 2:
                continue
            ibi_data = get_ipi_data(segment_ppg)
            if ibi_data.size < 2:
                tqdm.write(f"Insufficient IBI data in segment starting {start/SAMPLING_RATE} seconds of {csv_file}")
                continue
            af_detected, af_flags = detect_af(ibi_data)
            if af_detected:
                writer.writerow({
                    "file_name": csv_file,
                    "detected_time_segment": start,
                    "af_detected": af_detected,
                    "normalized_rmssd": af_flags["normalized_rmssd"],
                    "cv": af_flags["cv"],
                    "pnn50": af_flags["pnn50"]
                })
                tqdm.write(f"AF detected in {csv_file} at segment starting {start/SAMPLING_RATE} seconds")
                af_detected_ = True
                break
        if af_detected_:
            continue

    file.close()