import pandas as pd
import sounddevice as sd
import csv
import keyboard






def record_audio(file_name, sr=44100, channels=2):
    rec = []
    is_recording = false
    def callback(indata, frames, time, status):
        nonlocal rec, is_recording
        if is_recording:
            rec.append(indata.copy())
    with sd.InputStream(callback=callback, samplerate=sr, channels=channels):
        print('Press space to start recording')
        keyboard.wait('space')
        is_recording = True
        print('Recording... Press space to stop')
        keyboard.wait('space')
        is_recording = False
        print('Stopped recording now saving...')

        if rec:
        recorded_array = np.concatenate(rec, axis=0)
        sf.write(filename, recorded_array, samplerate)
        print(f"Saved to {filename}")
    else:
        print("No audio recorded.")


    def save_to_csv(data, file_name):

        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)
        print(f"Saved to {file_name}")\:
