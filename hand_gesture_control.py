import cv2
import mediapipe as mp
import pyautogui
import screen_brightness_control as sbc

# Initialize MediaPipe for hand tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Helper function to count fingers
def count_fingers(hand_landmarks):
    # Array of landmarks for fingers: thumb, index, middle, ring, pinky
    finger_tips = [4, 8, 12, 16, 20]
    finger_bases = [3, 6, 10, 14, 18]
    count = 0
    for tip, base in zip(finger_tips, finger_bases):
        # Check if the tip is above the base in the y-axis
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[base].y:
            count += 1
    return count

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
                # One finger up: increase brightness
                sbc.set_brightness(min(sbc.get_brightness()[0] + 10, 100))
            elif finger_count == 2:
                # Two fingers up: decrease brightness
                sbc.set_brightness(max(sbc.get_brightness()[0] - 10, 0))
            elif finger_count == 3 and previous_finger_count != 3:
                # Three fingers up: move to the next slide once
                pyautogui.press('right')
                previous_finger_count = 3  # Update previous count to avoid repeated triggers
            elif finger_count == 4 and previous_finger_count != 4:
                # Four fingers up: move to the previous slide once
                pyautogui.press('left')
                previous_finger_count = 4  # Update previous count to avoid repeated triggers
            elif finger_count == 5 and not continuous_slide_mode:
                # Five fingers up: activate continuous slide mode
                continuous_slide_mode = True
                previous_finger_count = 5  # Set previous count to prevent repeated triggers
            elif finger_count < 5:
                # Reset continuous mode if less than five fingers are shown
                continuous_slide_mode = False
                previous_finger_count = finger_count
            
            # Check continuous slide mode
            if continuous_slide_mode:
                pyautogui.press('right')
                
    # Display the image with landmarks
    cv2.imshow("Hand Gesture Recognition", image)
    
    # Exit the program if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting program...")
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
