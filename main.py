import cv2
import time
import os


def try_capture(index):
    print(f"Attempting to open camera at index {index}")
    cap = cv2.VideoCapture(index + cv2.CAP_DSHOW)
    if not cap.isOpened():
        print(f"Failed to open camera at index {index}")
        return None
    time.sleep(1)  # Delay to let camera initialize
    return cap


# Create images folder if it doesn't exist
if not os.path.exists('images'):
    os.makedirs('images')

# Define the size of the rectangle to capture
RECT_SIZE = (200, 200)  # Width and height of the rectangle

# Mapping of key presses to IDs
ID_MAP = {
    ord('w'): 'Forward',
    ord('a'): 'Turn LF',
    ord('d'): 'Turn RT',
    ord('2'): 'Two',
    ord('3'): 'Three',
    ord('4'): 'Four'
}

# Initialize current ID
current_id = 'Forward'

# Click event handler


def click_event(event, x, y, flags, param):
    global frame, current_id
    if event == cv2.EVENT_MOUSEMOVE:
        # Create a copy of the frame for previewing
        preview_frame = frame.copy()

        # Calculate the top-left corner of the rectangle
        top_left_x = max(0, x - RECT_SIZE[0] // 2)
        top_left_y = max(0, y - RECT_SIZE[1] // 2)

        # Calculate the bottom-right corner of the rectangle
        bottom_right_x = min(frame.shape[1], top_left_x + RECT_SIZE[0])
        bottom_right_y = min(frame.shape[0], top_left_y + RECT_SIZE[1])

        # Draw the rectangle on the preview frame
        cv2.rectangle(preview_frame, (top_left_x, top_left_y),
                      (bottom_right_x, bottom_right_y), (0, 255, 0), 2)

        # Display the preview frame with the rectangle
        cv2.imshow('frame', preview_frame)

    elif event == cv2.EVENT_LBUTTONDOWN:
        if 'frame' in globals():  # Check if 'frame' exists in global namespace
            # Calculate the top-left corner of the rectangle
            top_left_x = max(0, x - RECT_SIZE[0] // 2)
            top_left_y = max(0, y - RECT_SIZE[1] // 2)

            # Calculate the bottom-right corner of the rectangle
            bottom_right_x = min(frame.shape[1], top_left_x + RECT_SIZE[0])
            bottom_right_y = min(frame.shape[0], top_left_y + RECT_SIZE[1])

            # Extract the rectangular region
            region = frame[top_left_y:bottom_right_y,
                           top_left_x:bottom_right_x]

            # Generate a unique filename with current ID as prefix
            filename = f"images/{current_id}_{int(time.time())}.png"
            cv2.imwrite(filename, region)
            print(f"Image saved as {filename}")

            # Draw the rectangle on the frame (for visualization)
            cv2.rectangle(frame, (top_left_x, top_left_y),
                          (bottom_right_x, bottom_right_y), (0, 255, 0), 2)

            # Display the resulting frame
            cv2.imshow('frame', frame)


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

    # Display current ID in the bottom left corner
    font = cv2.FONT_HERSHEY_SIMPLEX
    bottom_left_corner = (10, frame.shape[0] - 10)
    font_scale = 0.5
    font_thickness = 1
    cv2.putText(frame, f'Current ID: {
                current_id}', bottom_left_corner, font, font_scale, (255, 255, 255), font_thickness)

    # Set mouse callback with lambda function to pass frame
    cv2.setMouseCallback('frame', lambda event, x, y, flags,
                         param: click_event(event, x, y, flags, param))

    # Display the initial frame
    cv2.imshow('frame', frame)

    # Check for key press events
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key in ID_MAP:
        current_id = ID_MAP[key]

    # Add a small delay to reduce CPU usage
    time.sleep(0.01)

# When everything done, release the capture
vid.release()
cv2.destroyAllWindows()
print("Program ended")
