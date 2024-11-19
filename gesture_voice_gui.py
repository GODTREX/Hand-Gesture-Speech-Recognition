import cv2
import mediapipe as mp
import pyautogui
import screen_brightness_control as sbc
import speech_recognition as sr
import pyttsx3
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import tkinter as tk
from tkinter import messagebox
from threading import Thread
import math
import time

# Initialize MediaPipe and Speech Recognition Components
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Initialize Audio Control for Volume
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Tkinter GUI setup
root = tk.Tk()
root.title("Hand Gesture and Voice Control")
root.geometry("500x400")

# Status label for actions
status_label = tk.Label(root, text="Status: Ready", font=("Helvetica", 16))
status_label.pack(pady=20)

# Variable to control the running state of the gesture/voice recognition
is_running = False

# Helper function to count fingers
def count_fingers(hand_landmarks):
    finger_tips = [4, 8, 12, 16, 20]
    finger_bases = [3, 6, 10, 14, 18]
    count = 0
    for tip, base in zip(finger_tips, finger_bases):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[base].y:
            count += 1
    return count

# Function to control volume
def adjust_volume(change):
    current_volume = volume.GetMasterVolumeLevelScalar()
    new_volume = max(0.0, min(1.0, current_volume + change))
    volume.SetMasterVolumeLevelScalar(new_volume, None)

# Function to recognize voice commands
def recognize_voice_command():
    with sr.Microphone() as source:
        print("Listening for command...")
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
        try:
            command = recognizer.recognize_google(audio).lower()
            print(f"Command received: {command}")
            return command
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            print("Could not request results from Speech Recognition service")
            return None

# Function to start gesture and voice recognition
def start_recognition():
    global is_running
    is_running = True
    status_label.config(text="Status: Running")
    Thread(target=run_recognition).start()

# Function to stop gesture and voice recognition
def stop_recognition():
    global is_running
    is_running = False
    status_label.config(text="Status: Stopped")

# Function to run gesture and voice recognition
def run_recognition():
    global is_running
    cap = cv2.VideoCapture(0)
    previous_finger_count = 0
    continuous_slide_mode = False
    
    while is_running and cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        # Flip the image horizontally for a mirrored view
        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        result = hands.process(image_rgb)

        # Process hand gestures
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                finger_count = count_fingers(hand_landmarks)

                # Perform actions based on finger count
                if finger_count == 1:
                    sbc.set_brightness(min(sbc.get_brightness()[0] + 10, 100))
                    status_label.config(text="Status: Brightness Increased")
                elif finger_count == 2:
                    sbc.set_brightness(max(sbc.get_brightness()[0] - 10, 0))
                    status_label.config(text="Status: Brightness Decreased")
                elif finger_count == 3 and previous_finger_count != 3:
                    pyautogui.press('right')
                    status_label.config(text="Status: Next Slide")
                    previous_finger_count = 3
                elif finger_count == 4 and previous_finger_count != 4:
                    pyautogui.press('left')
                    status_label.config(text="Status: Previous Slide")
                    previous_finger_count = 4
                elif finger_count == 5 and not continuous_slide_mode:
                    continuous_slide_mode = True
                    previous_finger_count = 5
                elif finger_count < 5:
                    continuous_slide_mode = False
                    previous_finger_count = finger_count

                # Continuous slide mode
                if continuous_slide_mode:
                    pyautogui.press('right')

        # Listen for voice commands
        command = recognize_voice_command()
        if command:
            if "next" in command:
                pyautogui.press('right')
                status_label.config(text="Status: Next Slide")
            elif "back" in command or "previous" in command:
                pyautogui.press('left')
                status_label.config(text="Status: Previous Slide")
            elif "increase" in command:
                sbc.set_brightness(min(sbc.get_brightness()[0] + 10, 100))
                status_label.config(text="Status: Brightness Increased")
            elif "decrease" in command:
                sbc.set_brightness(max(sbc.get_brightness()[0] - 10, 0))
                status_label.config(text="Status: Brightness Decreased")
            elif "loud" in command:
                adjust_volume(0.1)
                status_label.config(text="Status: Volume Increased")
            elif "lower" in command:
                adjust_volume(-0.1)
                status_label.config(text="Status: Volume Decreased")

        # Display the image
        cv2.imshow("Hand Gesture Recognition", image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    status_label.config(text="Status: Ready")

# Start and Stop buttons
start_button = tk.Button(root, text="Start", command=start_recognition, font=("Helvetica", 14), width=10)
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Stop", command=stop_recognition, font=("Helvetica", 14), width=10)
stop_button.pack(pady=10)

# Exit button
exit_button = tk.Button(root, text="Exit", command=root.quit, font=("Helvetica", 14), width=10)
exit_button.pack(pady=10)

root.mainloop()
