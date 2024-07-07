import cv2
import time
import os
import csv
import sys

RECT_SIZE = (200, 200)
ID_MAP = {
    ord('w'): 'Forward',
    ord('a'): 'Turn LF',
    ord('d'): 'Turn RT',
    ord('2'): 'Two',
    ord('3'): 'Three',
    ord('4'): 'Four'
}


def try_capture(index):
    """Attempt to open a camera at a specific index."""
    print(f"Attempting to open camera at index {index}")
    cap = cv2.VideoCapture(index + cv2.CAP_DSHOW)
    if not cap.isOpened():
        print(f"Failed to open camera at index {index}")
        return None
    time.sleep(1)
    return cap


def save_image_and_append_csv(image_folder, csv_file, frame, current_label, instance_id, x, y):
    """Save the captured image and append the label to the CSV file."""
    top_left_x = max(0, x - RECT_SIZE[0] // 2)
    top_left_y = max(0, y - RECT_SIZE[1] // 2)
    bottom_right_x = min(frame.shape[1], top_left_x + RECT_SIZE[0])
    bottom_right_y = min(frame.shape[0], top_left_y + RECT_SIZE[1])

    region = frame[top_left_y:bottom_right_y, top_left_x:bottom_right_x]
    filename = os.path.join(image_folder, f"{current_label}_{instance_id}.png")
    cv2.imwrite(filename, region)
    print(f"Image saved as {filename}")

    with open(csv_file, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([instance_id, current_label])


def click_event(event, x, y, flags, param):
    """Handle mouse click events to capture and save images."""
    data = param
    frame = data['frame']
    image_folder = data['image_folder']
    csv_file = data['csv_file']
    current_label = data['current_label']
    instance_id = data['instance_id']

    if event == cv2.EVENT_MOUSEMOVE:
        preview_frame = frame.copy()
        top_left_x = max(0, x - RECT_SIZE[0] // 2)
        top_left_y = max(0, y - RECT_SIZE[1] // 2)
        bottom_right_x = min(frame.shape[1], top_left_x + RECT_SIZE[0])
        bottom_right_y = min(frame.shape[0], top_left_y + RECT_SIZE[1])
        cv2.rectangle(preview_frame, (top_left_x, top_left_y),
                      (bottom_right_x, bottom_right_y), (0, 255, 0), 2)
        cv2.imshow('frame', preview_frame)
    elif event == cv2.EVENT_LBUTTONDOWN:
        save_image_and_append_csv(
            image_folder, csv_file, frame, current_label, instance_id, x, y)
        top_left_x = max(0, x - RECT_SIZE[0] // 2)
        top_left_y = max(0, y - RECT_SIZE[1] // 2)
        bottom_right_x = min(frame.shape[1], top_left_x + RECT_SIZE[0])
        bottom_right_y = min(frame.shape[0], top_left_y + RECT_SIZE[1])
        cv2.rectangle(frame, (top_left_x, top_left_y),
                      (bottom_right_x, bottom_right_y), (0, 255, 0), 2)
        cv2.imshow('frame', frame)
        data['instance_id'] += 1


def main():
    if len(sys.argv) != 3:
        print("Usage: capture.py <camera_index> <image_folder>")
        sys.exit(1)

    camera_index = int(sys.argv[1])
    image_folder = sys.argv[2]

    if not os.path.exists(image_folder):
        os.makedirs(image_folder)

    csv_file = os.path.join(image_folder, 'dataset.csv')
    if not os.path.exists(csv_file):
        with open(csv_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Label'])

    vid = try_capture(camera_index) if camera_index >= 0 else None
    if vid is None:
        for i in range(3):
            vid = try_capture(i)
            if vid is not None:
                break

    if vid is None:
        print("Could not open any camera")
        sys.exit(1)

    print("Camera opened successfully")

    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    data = {
        'frame': None,
        'image_folder': image_folder,
        'csv_file': csv_file,
        'current_label': 'Forward',
        'instance_id': 0
    }

    while True:
        ret, frame = vid.read()
        if not ret:
            print("Failed to grab frame")
            break

        if frame.shape[0] == 0 or frame.shape[1] == 0:
            print("Invalid frame dimensions")
            continue

        data['frame'] = frame
        cv2.putText(frame, f'Current Label: {
                    data["current_label"]}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow('frame', frame)
        cv2.setMouseCallback('frame', click_event, data)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key in ID_MAP:
            data['current_label'] = ID_MAP[key]

    vid.release()
    cv2.destroyAllWindows()
    print("Program ended")


if __name__ == "__main__":
    main()
