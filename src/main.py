import backend as bk
import os
import csv

# Define fieldnames for the CSV
fieldnames = ['path', 'speaker_id', 'severity', 'type', 'condition']

def getNextID(csv_path):
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        speakerIDs = set()
        for row in reader:
            try:
                speakerIDs.add(int(row['speaker_id']))
            except (ValueError, KeyError):
                continue
        
    if speakerIDs:
        return max(speakerIDs) + 1
    return 1

def main():
    with open("phrases.csv", "r") as file:
        phrases = file.readlines()
    
    base_path = "data"
    recsdir = os.path.join(base_path, 'recordings')
    os.makedirs(base_path, exist_ok=True)
    os.makedirs(recsdir, exist_ok=True)
    
    severity = input("Enter the severity: ")
    type_ = input("Enter the type: ")
    condition = input("Enter the condition: ")
    
    csv_path = os.path.join(base_path, 'metadata.csv')
    csvExists = os.path.isfile(csv_path)
    
    speakerID = getNextID(csv_path)
    speakerdir = os.path.join(base_path, str(speakerID))
    os.makedirs(speakerdir, exist_ok=True)
    
    with open(csv_path, 'a', newline='') as file:
        writer = csv.writer(file)
        if not csvExists:
            writer.writerow(["Speaker ID", "Severity", "Type", "Condition"])
        writer.writerow([speakerID, severity, type_, condition])
    
    for phrase in phrases:
        for take in range(1, 4):
            print(f"Recording {take} for phrase: {phrase.strip()}")
            # Display the phrase to the user
            print(phrase.strip())
            # Record audio (replace with actual recording code)
            filename = f"phrase_{phrases.index(phrase)+1}_take_{take}.wav"
            filepath = os.path.join(speakerdir, filename)
            bk.record_audio(filepath, duration=3, sample_rate=44100)
            # Write metadata to CSV
            csvpath = os.path.join('data', 'recordings', str(speakerID), filename)
            with open(csv_path, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow({
                    'path': csvpath,
                    'speaker_id': speakerID,
                    'severity': severity,
                    'type': type_,
                    'condition': condition
                })

if __name__ == "__main__":
    main()
