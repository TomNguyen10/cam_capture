import cv2
import time
import os
import numpy as np


def try_capture(index):
    print(f"Attempting to open camera at index {index}")
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        print(f"Failed to open camera at index {index}")
        return None
    return cap


# Create images folder if it doesn't exist
if not os.path.exists('images'):
    os.makedirs('images')

# Define the size of the rectangle to capture
RECT_SIZE = (200, 200)  # Width and height of the rectangle

# Click event handler


def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        # Calculate the top-left corner of the rectangle
        top_left_x = max(0, x - RECT_SIZE[0] // 2)
        top_left_y = max(0, y - RECT_SIZE[1] // 2)

        # Calculate the bottom-right corner of the rectangle
        bottom_right_x = min(frame.shape[1], top_left_x + RECT_SIZE[0])
        bottom_right_y = min(frame.shape[0], top_left_y + RECT_SIZE[1])

        # Extract the rectangular region
        region = frame[top_left_y:bottom_right_y, top_left_x:bottom_right_x]

        # Generate a unique filename
        filename = f"images/capture_{int(time.time())}.png"
        cv2.imwrite(filename, region)
        print(f"Image saved as {filename}")

        # Draw the rectangle on the frame (for visualization)
        cv2.rectangle(frame, (top_left_x, top_left_y),
                      (bottom_right_x, bottom_right_y), (0, 255, 0), 2)


# Try different camera indices
for i in range(3):  # Try indices 0, 1, and 2
    vid = try_capture(i)
    if vid is not None:
        break

if vid is None:
    print("Could not open any camera")
    exit()

print("Camera opened successfully")

# Create a named window and set mouse callback
cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
cv2.setMouseCallback('frame', click_event)

# Set up ArUco marker detection
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
params = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(dictionary, params)

print('ArUco detector set up')

while True:
    # Capture frame-by-frame
    ret, frame = vid.read()

    if not ret:
        print("Failed to grab frame")
        break

    # Check frame dimensions
    if frame.shape[0] == 0 or frame.shape[1] == 0:
        print("Invalid frame dimensions")
        continue

    # Detect ArUco markers
    corners, ids, rejected = detector.detectMarkers(frame)

    # If at least one marker is detected
    if ids is not None:
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

    # Display the resulting frame
    cv2.imshow('frame', frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Add a small delay to reduce CPU usage
    time.sleep(0.01)

# When everything done, release the capture
vid.release()
cv2.destroyAllWindows()
print("Program ended")
