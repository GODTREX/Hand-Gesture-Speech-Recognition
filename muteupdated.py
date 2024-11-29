import threading
import pyautogui
import speech_recognition as sr
import screen_brightness_control as sbc
import time
import tkinter as tk
import cv2
import mediapipe as mp
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL

# Global variable for managing the running status
running = True

# Initialize MediaPipe Hand detection
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Volume Control Setup
def change_volume(action):
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)

        if action == "increase":
            current_volume = volume.GetMasterVolumeLevelScalar()
            volume.SetMasterVolumeLevelScalar(min(1.0, current_volume + 0.1), None)
        elif action == "decrease":
            current_volume = volume.GetMasterVolumeLevelScalar()
            volume.SetMasterVolumeLevelScalar(max(0.0, current_volume - 0.1), None)
        elif action == "max":
            volume.SetMasterVolumeLevelScalar(1.0, None)  # Maximum volume
        elif action == "mute":
            volume.SetMute(1, None)  # Mute volume
    except Exception as e:
        print(f"Error adjusting volume: {e}")

# Perform actions based on finger count
def perform_action(finger_count):
    print(f"Finger Count: {finger_count}")
    try:
        current_brightness = sbc.get_brightness()[0] if isinstance(sbc.get_brightness(), list) else sbc.get_brightness()

        if finger_count == 0:
            change_volume("mute")  # Mute volume
            print("Volume muted.")
        elif finger_count == 1:
            sbc.set_brightness(min(100, current_brightness + 10))  # Increase brightness
            print("Brightness increased.")
        elif finger_count == 2:
            sbc.set_brightness(max(0, current_brightness - 10))  # Decrease brightness
            print("Brightness decreased.")
        elif finger_count == 3:
            pyautogui.press('right')  # Next slide
            print("Next slide.")
        elif finger_count == 4:
            pyautogui.press('left')  # Previous slide
            print("Previous slide.")
        elif finger_count == 5:
            change_volume("max")  # Set volume to max
            print("Volume set to maximum.")
    except Exception as e:
        print(f"Error in perform_action: {e}")

# Count fingers
def count_fingers(landmarks):
    """
    Counts the number of fingers raised based on the hand landmarks.
    """
    # Tip and MCP indices for all five fingers
    finger_tips = [4, 8, 12, 16, 20]
    finger_mcp = [3, 6, 10, 14, 18]

    count = 0
    for tip, mcp in zip(finger_tips, finger_mcp):
        # Check if the fingertip is above the MCP (for raised finger)
        if landmarks.landmark[tip].y < landmarks.landmark[mcp].y:
            count += 1

    # Special condition: If all fingertips are below their respective MCPs, count as 0 (closed fist)
    if count == 0:
        all_below = all(landmarks.landmark[tip].y > landmarks.landmark[mcp].y for tip, mcp in zip(finger_tips, finger_mcp))
        if all_below:
            return 0

    return count

# Voice command actions
def perform_voice_action(command):
    command = command.lower()
    if "louder" in command:
        change_volume("increase")
        print("Volume increased.")
    elif "lower" in command:
        change_volume("decrease")
        print("Volume decreased.")
    elif "next" in command:
        pyautogui.press('right')
        print("Next slide.")
    elif "previous" in command or "back" in command:
        pyautogui.press('left')
        print("Previous slide.")
    elif "exit" in command:
        print("Exiting...")
        global running
        running = False
        root.quit()

# Voice recognition thread
def listen_for_voice_commands():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    while running:
        with mic as source:
            print("Listening for commands...")
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=5)
                command = recognizer.recognize_google(audio)
                print(f"Voice Command: {command}")
                perform_voice_action(command)
            except sr.WaitTimeoutError:
                pass
            except sr.UnknownValueError:
                print("Could not understand audio.")
            except sr.RequestError as e:
                print(f"Error with speech recognition: {e}")
        time.sleep(1)

# Camera thread
def camera_thread():
    cap = cv2.VideoCapture(0)
    while running:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                finger_count = count_fingers(hand_landmarks)
                perform_action(finger_count)
        cv2.imshow("Hand Gesture Control", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

# GUI functions
def create_gui():
    global root
    root = tk.Tk()
    root.title("Hand Gesture Control Application")
    label = tk.Label(root, text="Application Running...", font=("Arial", 14))
    label.pack(pady=20)
    start_button = tk.Button(root, text="Start", command=start_app, font=("Arial", 12))
    start_button.pack(pady=10)
    stop_button = tk.Button(root, text="Stop", command=stop_app, font=("Arial", 12))
    stop_button.pack(pady=10)
    exit_button = tk.Button(root, text="Exit", command=exit_app, font=("Arial", 12))
    exit_button.pack(pady=10)
    root.mainloop()

def start_app():
    global running
    running = True
    threading.Thread(target=listen_for_voice_commands, daemon=True).start()
    threading.Thread(target=camera_thread, daemon=True).start()
    print("Application started.")

def stop_app():
    global running
    running = False
    print("Application stopped.")

def exit_app():
    global running
    running = False
    print("Exiting...")
    root.quit()

if __name__ == "__main__":
    create_gui()
