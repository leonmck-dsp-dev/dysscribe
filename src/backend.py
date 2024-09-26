# backend.py

import os
import csv
import sounddevice as sd
import soundfile as sf

# Define fieldnames for the CSV
FIELDNAMES = ['path', 'speaker_id', 'severity', 'type', 'condition', 'phrase']

def list_input_devices():
    print("Available input devices:")
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"{idx}: {device['name']}")

def select_input_device():
    list_input_devices()
    while True:
        try:
            device_input = input("Enter the index of the input device you want to use: ")
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
    audio_data = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=channels,
        dtype='int16',
        device=device
    )
    sd.wait()
    sf.write(filename, audio_data, sample_rate)
    print("Recording complete.")

def run():
    phrases = [
        "Hello, my name is John.",
        "I am a student at the University of Toronto.",
        "I am studying computer science.",
        "I am in my fourth year.",
        "I am from Toronto.",
        "I am interested in machine learning.",
        "I am looking for a job in software development.",
        "I am excited to graduate.",
        "I am looking forward to the future.",
        "I am happy to be here."
    ]
    base_path = "data"
    recsdir = os.path.join(base_path, 'recordings')
    os.makedirs(base_path, exist_ok=True)
    os.makedirs(recsdir, exist_ok=True)

    severity = input("Enter the severity: ")
    type_ = input("Enter the type: ")
    condition = input("Enter the condition: ")

    # Select the input device
    device_index = select_input_device()

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
            print(f"\nRecording {take} for phrase: {phrase.strip()}")
            # Display the phrase to the user
            print("Please read the following phrase:")
            print(f"\"{phrase.strip()}\"")
            input("Press Enter when you're ready to start recording...")
            # Record audio
            filename = f"phrase_{phrases.index(phrase)+1}_take_{take}.wav"
            filepath = os.path.join(speakerdir, filename)
            record_audio(filepath, duration=3, sample_rate=44100, device=device_index)
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