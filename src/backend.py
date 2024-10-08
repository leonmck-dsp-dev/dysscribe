# backend.py

import os
import csv
import sounddevice as sd
import soundfile as sf
import ipywidgets as widgets

# Define fieldnames for the CSV
FIELDNAMES = ['path', 'speaker_id', 'severity', 'type', 'condition', 'phrase']
# sample phrases - TODO: Add The csv phrases list here  

# bool to start recording each phrase take
recording = False

# Function to connect bool to button click
def start_recording(b):
    global recording
    recording = True
phrases = ["Hello, how are you?", "What is your name?", "Where are you from?", "How old are you?", "What is your favorite color?"]

def get_phrase():
    for phrase in phrases:
        return phrase.strip()
def list_input_devices():
    print("Available input devices:")
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"{idx}: {device['name']}")

def select_input_device(device_input):
    list_input_devices()
    while True:
        try:
            device_index = int(device_input)
            device = sd.query_devices(device_index)
            if device['max_input_channels'] > 0:
                return device_index
            else:
                print("The selected device is not an input device. Please choose again.")
        except (ValueError, IndexError):
            print("Invalid input. Please enter a valid device index.")

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

def record_audio(filename, duration=3, sample_rate=44100, channels=1, device=None):
    print("Recording...")
    devices = sd.query_devices()
    for idx, dev in enumerate(devices):
        print(f"{idx}: {dev['name']}")
    max_input_channels = devices[device]['max_input_channels']
    if channels > max_input_channels:
        print(f"Reducing number of input channels from {channels} to {max_input_channels}")
        channels = max_input_channels
    audio_data = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=max_input_channels,
        dtype='int16',
        device=device
    )
    sd.wait()
    sf.write(filename, audio_data, sample_rate)
    print("Recording complete.")

def run(severity, type_, condition , device):
    base_path = "data"
    recsdir = os.path.join(base_path, 'recordings')
    os.makedirs(base_path, exist_ok=True)
    os.makedirs(recsdir, exist_ok=True)

    severity = severity
    type_ = type_
    condition = condition 
    csv_path = os.path.join(base_path, 'metadata.csv')
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
            # reset recording bool each take
            recording = False
            if recording:
                continue             
            filename = f"phrase_{phrases.index(phrase)+1}_take_{take}.wav"
            filepath = os.path.join(speakerdir, filename)
            record_audio(filepath, duration=3, sample_rate=44100, device=device)
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