# gui.py

import tkinter as tk
from tkinter import messagebox, ttk
import backend as bk  # Import your backend module
import csv
import os

class RecordingApp:
    def __init__(self, master):
        self.master = master
        master.title("Recording Application")

        # Initialize variables
        self.severity = tk.StringVar()
        self.type_ = tk.StringVar()
        self.condition = tk.StringVar()
        self.device_index = tk.IntVar()
        self.phrase_index = 0
        self.take = 1
        self.speakerID = None
        self.selected_phrases = []
        self.base_path = "data"
        self.recsdir = os.path.join(self.base_path, 'recordings')
        self.csv_path = os.path.join(self.base_path, 'metadata.csv')
        self.device_list = []

        # Create directories if they don't exist
        os.makedirs(self.recsdir, exist_ok=True)

        # Predefined options
        self.severity_options = ["Mild", "Moderate", "Severe"]
        self.type_options = ["Type A", "Type B", "Type C"]
        self.condition_options = ["Condition X", "Condition Y", "Condition Z"]

        self.all_phrases = [
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

        # Set up the GUI layout
        self.create_widgets()

    def create_widgets(self):
        # Dropdown menus for severity, type, and condition
        tk.Label(self.master, text="Severity:").grid(row=0, column=0, sticky='e')
        self.severity_menu = ttk.Combobox(self.master, textvariable=self.severity, values=self.severity_options, state='readonly')
        self.severity_menu.grid(row=0, column=1)

        tk.Label(self.master, text="Type:").grid(row=1, column=0, sticky='e')
        self.type_menu = ttk.Combobox(self.master, textvariable=self.type_, values=self.type_options, state='readonly')
        self.type_menu.grid(row=1, column=1)

        tk.Label(self.master, text="Condition:").grid(row=2, column=0, sticky='e')
        self.condition_menu = ttk.Combobox(self.master, textvariable=self.condition, values=self.condition_options, state='readonly')
        self.condition_menu.grid(row=2, column=1)

        # Listbox for phrases selection
        tk.Label(self.master, text="Select Phrases:").grid(row=3, column=0, columnspan=2)
        self.phrases_listbox = tk.Listbox(self.master, selectmode=tk.MULTIPLE, width=50, height=10)
        self.phrases_listbox.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        for phrase in self.all_phrases:
            self.phrases_listbox.insert(tk.END, phrase)

        # Button to select input device
        tk.Button(self.master, text="Select Input Device", command=self.select_device).grid(row=5, column=0, columnspan=2)

        # Start recording button
        tk.Button(self.master, text="Start Recording", command=self.start_recording).grid(row=6, column=0, columnspan=2, pady=5)

        # Label to display phrases
        self.phrase_label = tk.Label(self.master, text="", wraplength=400)
        self.phrase_label.grid(row=7, column=0, columnspan=2, pady=10)

        # Record button
        self.record_button = tk.Button(self.master, text="Record", state='disabled', command=self.record_phrase)
        self.record_button.grid(row=8, column=0, columnspan=2)

    def select_device(self):
        # Use backend function to list and select devices
        devices = bk.sd.query_devices()
        self.device_list = [device for device in devices if device['max_input_channels'] > 0]

        # Create a new window for device selection
        device_window = tk.Toplevel(self.master)
        device_window.title("Select Input Device")

        tk.Label(device_window, text="Available Input Devices:").pack()

        # Variable to hold selected device index
        self.selected_device = tk.IntVar(value=-1)

        # List available devices with radio buttons
        for idx, device in enumerate(self.device_list):
            device_name = device['name']
            tk.Radiobutton(
                device_window,
                text=f"{idx}: {device_name}",
                variable=self.selected_device,
                value=idx
            ).pack(anchor='w')

        tk.Button(device_window, text="Confirm", command=device_window.destroy).pack(pady=5)

    def start_recording(self):
        if not self.severity.get() or not self.type_.get() or not self.condition.get():
            messagebox.showwarning("Input Required", "Please select severity, type, and condition.")
            return

        # Get selected phrases from the listbox
        selected_indices = self.phrases_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Input Required", "Please select at least one phrase.")
            return
        self.selected_phrases = [self.phrases_listbox.get(i) for i in selected_indices]

        # Check if a device has been selected
        if not hasattr(self, 'selected_device') or self.selected_device.get() == -1:
            messagebox.showwarning("Device Selection", "Please select an input device.")
            return

        # Get speaker ID
        self.speakerID = bk.get_next_id(self.csv_path, self.recsdir)
        self.speakerdir = os.path.join(self.recsdir, str(self.speakerID))
        os.makedirs(self.speakerdir, exist_ok=True)

        # Write CSV header if file doesn't exist
        if not os.path.isfile(self.csv_path):
            with open(self.csv_path, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=bk.FIELDNAMES)
                writer.writeheader()

        # Initialize phrase index and take
        self.phrase_index = 0
        self.take = 1

        # Update the phrase display and enable the record button
        self.update_phrase_display()
        self.record_button.config(state='normal')

    def update_phrase_display(self):
        if self.phrase_index < len(self.selected_phrases):
            phrase = self.selected_phrases[self.phrase_index]
            self.phrase_label.config(text=f"Phrase {self.phrase_index + 1}, Take {self.take}:\n\"{phrase}\"")
        else:
            messagebox.showinfo("Recording Complete", "All phrases have been recorded.")
            self.record_button.config(state='disabled')

    def record_phrase(self):
        phrase = self.selected_phrases[self.phrase_index]
        filename = f"phrase_{self.phrase_index + 1}_take_{self.take}.wav"
        filepath = os.path.join(self.speakerdir, filename)

        # Get the selected device index
        device_idx = self.selected_device.get()
        device_info = self.device_list[device_idx]
        device_index = device_info['index']

        # Record audio using backend function
        bk.record_audio(filepath, duration=3, sample_rate=44100, device=device_index)

        # Write metadata to CSV
        csvpath = os.path.join('recordings', str(self.speakerID), filename)
        with open(self.csv_path, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=bk.FIELDNAMES)
            writer.writerow({
                'path': csvpath,
                'speaker_id': self.speakerID,
                'severity': self.severity.get(),
                'type': self.type_.get(),
                'condition': self.condition.get(),
                'phrase': phrase.strip()
            })

        # Update take and phrase index
        if self.take < 3:
            self.take += 1
        else:
            self.take = 1
            self.phrase_index += 1
        self.update_phrase_display()

if __name__ == "__main__":
    root = tk.Tk()
    app = RecordingApp(root)
    root.mainloop()
