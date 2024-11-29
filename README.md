Here is an **updated README** file for your GitHub repository that includes all the recent features, including hand gestures and voice control:

---

# Hand Gesture & Voice Control Application

This application allows you to control your system's volume and other functions like brightness, slideshows, and more using **hand gestures** and **voice commands**. You can increase or decrease the system volume, mute it, and even change screen brightness, all using your hands or voice. 

### Features
- **Hand Gestures**:
  - **0 fingers (Fist)**: Volume decreases to zero.
  - **1 finger**: Increase brightness.
  - **2 fingers**: Decrease brightness.
  - **3 fingers**: Move to the next slide (right arrow key).
  - **4 fingers**: Move to the previous slide (left arrow key).
  - **5 fingers**: Set volume to maximum.

- **Voice Commands**:
  - **"Louder"**: Increases the system volume.
  - **"Lower"**: Decreases the system volume.
  - **"Next"**: Moves to the next slide (right arrow key).
  - **"Previous" / "Back"**: Moves to the previous slide (left arrow key).
  - **"Max volume"**: Sets the system volume to maximum.
  - **"Mute volume"**: Sets the system volume to zero.
  - **"Exit"**: Exits the application.

### Prerequisites

- Python 3.x
- Install the required libraries using `pip` or `pipenv`.

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/Hand-Gesture-Speech-Recognition.git
   cd Hand-Gesture-Speech-Recognition
   ```

2. Install the necessary dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   The `requirements.txt` file includes:
   - `mediapipe` (for hand gesture detection)
   - `pyautogui` (for controlling the system's volume and keyboard keys)
   - `speechrecognition` (for voice command recognition)
   - `pycaw` (for volume control)
   - `screen-brightness-control` (for controlling the screen brightness)
   - `opencv-python` (for video capture)
   - `tkinter` (for GUI)

### Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. The GUI will appear with an option to start the application. Once started, the application will use your webcam to detect hand gestures and listen for voice commands.

3. Hand gestures:
   - Show your hand in front of the camera, and the application will detect the number of fingers raised.
   - Each gesture corresponds to an action like adjusting the volume or changing brightness.

4. Voice commands:
   - Speak commands such as "max volume," "mute volume," "next," "previous," and others to control the system's volume and other features.

5. Press **"q"** to exit the camera view or click **"Exit"** in the GUI to stop the application.

### Troubleshooting

1. **Error: "PyAudio module not found"**:
   - Install `PyAudio` by running:
     ```bash
     pip install pyaudio
     ```
   - On Windows, you can also use `pipwin` to install `pyaudio`:
     ```bash
     pip install pipwin
     pipwin install pyaudio
     ```

2. **Camera not detected or working**:
   - Ensure your webcam is properly connected.
   - Try closing other applications that may be using the camera.

3. **Voice recognition errors**:
   - Make sure your microphone is working and properly configured.
   - Adjust the ambient noise levels if needed using the `recognizer.adjust_for_ambient_noise()` function.

### Contributing

Contributions are welcome! Please fork the repository, create a new branch, and submit a pull request with any improvements, bug fixes, or new features.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Acknowledgments

- **MediaPipe**: For hand gesture detection.
- **PyAudio**: For voice command processing.
- **PyCaw**: For controlling system volume.
- **OpenCV**: For video capture and processing.

---

This README file should provide a clear understanding of the project's functionality, setup instructions, and usage. Let me know if you'd like to make further changes!

(Note to self)
Doesn't work on latest python,used python 3.11 in this project
