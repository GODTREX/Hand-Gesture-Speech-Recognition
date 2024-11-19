import cv2
import mediapipe as mp
import pyautogui
import screen_brightness_control as sbc
import speech_recognition as sr
import pyttsx3
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import math

# Initialize MediaPipe for hand tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Initialize text-to-speech engine (optional for feedback)
engine = pyttsx3.init()

# Initialize volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Set up recognizer for voice commands
recognizer = sr.Recognizer()

# Helper function to count fingers
def count_fingers(hand_landmarks):
    # Array of landmarks for fingers: thumb, index, middle, ring, pinky
    finger_tips = [4, 8, 12, 16, 20]
    finger_bases = [3, 6, 10, 14, 18]
    count = 0
    for tip, base in zip(finger_tips, finger_bases):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[base].y:
            count += 1
    return count

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

# Function to control volume
def adjust_volume(change):
    current_volume = volume.GetMasterVolumeLevelScalar()
    new_volume = max(0.0, min(1.0, current_volume + change))
    volume.SetMasterVolumeLevelScalar(new_volume, None)

# Initialize video capture
cap = cv2.VideoCapture(0)

# Variables to track previous finger count for one-time actions
previous_finger_count = 0
continuous_slide_mode = False

while cap.isOpened():
    success, image = cap.read()
    if not success:
        break

    # Flip the image horizontally for a mirrored view
    image = cv2.flip(image, 1)

    # Convert the image color to RGB as required by MediaPipe
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Process the image and find hands
    result = hands.process(image_rgb)

    # Check if hands are detected
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Draw landmarks on the image
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Count the number of raised fingers
            finger_count = count_fingers(hand_landmarks)

            # Perform actions based on finger count with conditions for one-time actions
            if finger_count == 1:
                sbc.set_brightness(min(sbc.get_brightness()[0] + 10, 100))
                engine.say("Brightness increased")
                engine.runAndWait()
            elif finger_count == 2:
                sbc.set_brightness(max(sbc.get_brightness()[0] - 10, 0))
                engine.say("Brightness decreased")
                engine.runAndWait()
            elif finger_count == 3 and previous_finger_count != 3:
                pyautogui.press('right')
                previous_finger_count = 3
            elif finger_count == 4 and previous_finger_count != 4:
                pyautogui.press('left')
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

    # Display the image with landmarks
    cv2.imshow("Hand Gesture Recognition", image)

    # Listen for voice commands and act accordingly
    command = recognize_voice_command()
    if command:
        if "next" in command:
            pyautogui.press('right')
        elif "back" in command or "previous" in command:
            pyautogui.press('left')
        elif "increase" in command:
            sbc.set_brightness(min(sbc.get_brightness()[0] + 10, 100))
            engine.say("Brightness increased")
            engine.runAndWait()
        elif "decrease" in command:
            sbc.set_brightness(max(sbc.get_brightness()[0] - 10, 0))
            engine.say("Brightness decreased")
            engine.runAndWait()
        elif "loud" in command:
            adjust_volume(0.1)
            engine.say("Volume increased")
            engine.runAndWait()
        elif "lower" in command:
            adjust_volume(-0.1)
            engine.say("Volume decreased")
            engine.runAndWait()

    # Exit the program if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting program...")
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
