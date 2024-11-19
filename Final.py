import cv2
import threading
import queue
import time
import speech_recognition as sr
import pyautogui
import screen_brightness_control as sbc
from mediapipe import solutions
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Initialize components
hand_detection = solutions.hands.Hands()
recognizer = sr.Recognizer()

# Queue for frames and recognized text
frame_queue = queue.Queue()
voice_text_queue = queue.Queue()

# Global control variables
running = True
slide_advance_active = False

# Initialize audio endpoint for volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Detect the number of fingers
def count_fingers(hand_landmarks):
    tips_ids = [4, 8, 12, 16, 20]
    finger_states = []
    for i in range(1, 5):
        if hand_landmarks.landmark[tips_ids[i]].y < hand_landmarks.landmark[tips_ids[i] - 2].y:
            finger_states.append(1)
        else:
            finger_states.append(0)
    return sum(finger_states)

# Perform actions based on number of fingers
def perform_action(finger_count):
    global slide_advance_active
    try:
        if finger_count == 1:
            brightness = sbc.get_brightness(display=0)  # Get brightness for primary monitor
            sbc.set_brightness(min(brightness[0] + 10, 100), display=0)  # Increase brightness
        elif finger_count == 2:
            brightness = sbc.get_brightness(display=0)
            sbc.set_brightness(max(brightness[0] - 10, 0), display=0)  # Decrease brightness
        elif finger_count == 3:
            pyautogui.press("right")  # Next PowerPoint slide
        elif finger_count == 4:
            pyautogui.press("left")  # Previous PowerPoint slide
        elif finger_count == 5:
            slide_advance_active = True  # Activate continuous slide advance
    except Exception as e:
        print(f"Error in brightness or slide control: {e}")

# Voice command actions
def perform_voice_action(command):
    global running
    if "louder" in command:
        current_volume = volume.GetMasterVolumeLevelScalar()
        volume.SetMasterVolumeLevelScalar(min(current_volume + 0.1, 1.0), None)
    elif "lower" in command:
        current_volume = volume.GetMasterVolumeLevelScalar()
        volume.SetMasterVolumeLevelScalar(max(current_volume - 0.1, 0.0), None)
    elif "next" in command:
        pyautogui.press("right")
    elif "previous" in command or "back" in command:
        pyautogui.press("left")
    elif "exit" in command:
        print("Exiting...")
        running = False


# Camera processing thread
def camera_thread():
    global running, slide_advance_active
    cap = cv2.VideoCapture(0)
    while running:
        ret, frame = cap.read()
        if not ret:
            print("Camera could not be accessed.")
            break

        frame = cv2.resize(frame, (640, 480))
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hand_detection.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, solutions.hands.HAND_CONNECTIONS)
                finger_count = count_fingers(hand_landmarks)
                perform_action(finger_count)
        
        frame_queue.put(frame)
        time.sleep(0.03)

        if slide_advance_active:
            pyautogui.press("right")
            time.sleep(0.5)

    cap.release()

# Voice recognition thread
def voice_recognition_thread():
    global running
    mic = sr.Microphone()
    while running:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)
        
        try:
            text = recognizer.recognize_google(audio).lower()
            voice_text_queue.put(text)
            perform_voice_action(text)
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"Error with Google Speech Recognition: {e}")
        
        time.sleep(1)

# GUI display thread
def display_gui():
    global running
    cv2.namedWindow("Hand Gesture and Voice Recognition")
    while running:
        if not frame_queue.empty():
            frame = frame_queue.get()
            cv2.imshow("Hand Gesture and Voice Recognition", frame)
        
        if not voice_text_queue.empty():
            text = voice_text_queue.get()
            print(f"Voice Command: {text}")
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False
    
    cv2.destroyAllWindows()

# Start threads
camera_thread = threading.Thread(target=camera_thread)
voice_thread = threading.Thread(target=voice_recognition_thread)
gui_thread = threading.Thread(target=display_gui)

camera_thread.start()
voice_thread.start()
gui_thread.start()

# Wait for all threads to complete
camera_thread.join()
voice_thread.join()
gui_thread.join()
