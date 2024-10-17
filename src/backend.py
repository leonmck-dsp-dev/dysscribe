# backend.py

import os
import csv
import sounddevice as sd
import soundfile as sf
import ipywidgets as widgets
import threading
import time
import keyboard
# Define fieldnames for the CSV
FIELDNAMES = ['path', 'speaker_id', 'severity', 'type', 'condition', 'phrase']
# sample phrases - TODO: Add The csv phrases list here  
PhrasecsvPath = ""
DataCsvPath = ""
base_path = ""
def get_phrase(csv):
    with open(csv, 'r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            for phrase in row:  # Yield each phrase in a row
                yield phrase

sd.default.device = 'MacBook Pro Microphone'    # Default device to record from

    
def list_input_devices():
    print("Available input devices:")
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"{idx}: {device['name']}")

def select_input_device(preferred_device=sd.default.device):
    """
    Allows the user to select an input device from the available options,
    excluding HDMI devices.

    Args:
        preferred_device: The preferred device to use, if available. 
                          Can be an integer index or an sd._InputOutputPair.

    Returns:
        The selected input device index or None if no device is selected.
    """

    devices = sd.query_devices()
    print("Available audio input devices (excluding HDMI):")

    # Filter out HDMI devices
    input_devices = [dev for dev in devices if "HDMI" not in dev['name']]
    # If preferred_device is a string, try to find the device by name
    if isinstance(preferred_device, str):
        for idx, device in enumerate(devices):
            if device['name'] == preferred_device:
                return idx
        print(f"Device '{preferred_device}' not found.")
        return None

    # If preferred_device is an integer, it's an index
    elif isinstance(preferred_device, int):
        if preferred_device < len(devices):
            return preferred_device
        else:
            print(f"Device index {preferred_device} out of range.")
            return None

    # If preferred_device is an _InputOutputPair, return the input device index
    elif isinstance(preferred_device, sd._InputOutputPair):
        return preferred_device[0]

    else:
        print("Invalid preferred_device type.")
        return None
    
def get_next_id(csv_path, recsdir):
    # Collect IDs from CSV
    csv_speakerIDs = set()
    if os.path.isfile(csv_path):
        with open(csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    csv_speakerIDs.add(int(row['speaker_id']))
                except (ValueError, KeyError):
                    continue

    # Collect IDs from existing directories
    dir_speakerIDs = set()
    if os.path.isdir(recsdir):
        for name in os.listdir(recsdir):
            dir_path = os.path.join(recsdir, name)
            if os.path.isdir(dir_path):
                try:
                    dir_speakerIDs.add(int(name))
                except ValueError:
                    continue

    # Combine IDs from CSV and directories
    existingIDs = csv_speakerIDs.union(dir_speakerIDs)

    # Find the smallest unused ID starting from 1
    speakerID = 1
    while speakerID in existingIDs:
        speakerID += 1
    return speakerID 
def record_audio(filename, duration=30, sample_rate=44100, channels=1, device=sd.default.device):
    print("Recording...")
    devices = select_input_device(device) 
    # Extract the input device index
    if isinstance(device, sd._InputOutputPair):
        input_device_index = device[0]  # Get the index from the pair
    else:
        input_device_index = device  # Assume it's already an index 
    audio_data = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=channels, 
        dtype='int16',
        device=input_device_index  # Use the index here
    )
    sd.wait()
    sf.write(filename, audio_data, sample_rate)
    print("Recording complete.")

def listen_for_space():
    global stop_recording
    while True:
        if keyboard.is_pressed('space'):
            if stop_recording:
                print("Starting recording...")
            else:
                print("Stopping recording...")
            stop_recording = not stop_recording
            time.sleep(0.5)  # Debounce the space bar
def run(severity, type_, condition , device):
    recsdir = os.path.join(base_path, 'recordings')
    os.makedirs(base_path, exist_ok=True)
    os.makedirs(recsdir, exist_ok=True)

    severity = severity
    type_ = type_
    condition = condition 
    csv_path = os.path.join(base_path, DataCsvPath)
    csv_exists = os.path.isfile(csv_path)

    # If the CSV file does not exist, write the header
    if not csv_exists:
        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            writer.writeheader()

    speakerID = get_next_id(csv_path, recsdir)
    speakerdir = os.path.join(recsdir, str(speakerID))
    os.makedirs(speakerdir, exist_ok=True)

                
    for phrase in phrases:
        for take in range(1, 4):
            filename = f"phrase_{phrases.index(phrase)+1}_take_{take}.wav"
            filepath = os.path.join(speakerdir, filename)

            # Start recording in a separate thread
            record_thread = threading.Thread(target=record_audio, args=(filepath, 44100, 1,device))
            record_thread.start()
            record_thread.join()
        
            # Write metadata to CSV
            csvpath = os.path.join('recordings', str(speakerID), filename)
            with open(csv_path, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
                writer.writerow({
                    'path': csvpath,
                    'speaker_id': speakerID,
                    'severity': severity,
                    'type': type_,
                    'condition': condition,
                    'phrase': phrase.strip()
                })

if __name__ == "__main__":
    run()