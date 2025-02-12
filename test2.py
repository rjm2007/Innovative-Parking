import cv2
import numpy as np
import cvzone
import torch
import pickle
import threading  # For non-blocking save

print('Setup complete. Using torch %s %s' % (
    torch.__version__, torch.cuda.get_device_properties(0) if torch.cuda.is_available() else 'CPU'
))

cap = cv2.VideoCapture(r'C:\Users\rudra\Desktop\MLProjects\Innovative Parking\easy1.mp4')

drawing = False
temp_points = []  # Temporary storage for ongoing annotation
polylines = []
area_names = []

# Load existing data
try:
    with open('parking', 'rb') as f:
        data = pickle.load(f)
        polylines, area_names = data['polylines'], data['area_names']
except (FileNotFoundError, EOFError, KeyError):
    polylines, area_names = [], []

def draw(event, x, y, flags, param):
    """Handles mouse events for drawing polygons"""
    global drawing, temp_points

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        temp_points = [(x, y)]  # Start a new polygon

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        temp_points.append((x, y))

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        if len(temp_points) > 2:  # Only save if it's a valid polygon
            name = input("Enter area name: ")  # Ask for name AFTER drawing
            if name:
                area_names.append(name)
                polylines.append(np.array(temp_points, np.int32))
            temp_points = []  # Reset temp storage

def save_data():
    """Save polylines and area names in a separate thread to prevent UI lag"""
    data = {'polylines': polylines, 'area_names': area_names}
    with open('parking', 'wb') as f:
        pickle.dump(data, f)
    print("Data saved successfully!")

while True:
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    frame = cv2.resize(frame, (1020, 500), interpolation=cv2.INTER_LINEAR)

    # Draw existing polylines and labels
    for i, polyline in enumerate(polylines):
        cv2.polylines(frame, [polyline], True, (0, 0, 255), 2)
        cvzone.putTextRect(frame, f'{area_names[i]}', tuple(polyline[0]), 1, 1)

    cv2.imshow('Frame', frame)
    cv2.setMouseCallback('Frame', draw)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):
        threading.Thread(target=save_data, daemon=True).start()  # Non-blocking save

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

