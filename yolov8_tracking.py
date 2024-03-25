import sys
from collections import defaultdict
import cv2
import numpy as np
from ultralytics import YOLO

# Handling command line arguments
if len(sys.argv) < 2:
    print("Usage: python yolo_tracking.py <video_path>")
    sys.exit(1)
video_path = sys.argv[1]  # Get video path from command line argument

# Load the YOLOv8 model
model = YOLO('yolov8n.pt')

# Open the video file
cap = cv2.VideoCapture(video_path)

# Initialize video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
output_video_path = video_path.split('.')[0] + '_tracked.mp4'  # Output file name with '_tracked' suffix
frame_rate = cap.get(cv2.CAP_PROP_FPS)
frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
out = cv2.VideoWriter(output_video_path, fourcc, frame_rate, frame_size)

# Store the track history
track_history = defaultdict(lambda: [])

while cap.isOpened():
    success, frame = cap.read()
    if success:
        results = model.track(frame, persist=True)

        if results[0].boxes and results[0].boxes.id is not None:
            boxes = results[0].boxes.xywh.cpu()
            track_ids = results[0].boxes.id.int().cpu().tolist()

            annotated_frame = results[0].plot()

            for box, track_id in zip(boxes, track_ids):
                x, y, w, h = box
                track = track_history[track_id]
                track.append((float(x), float(y)))
                if len(track) > 30:
                    track.pop(0)
                
                points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
                cv2.polylines(annotated_frame, [points], isClosed=False, color=(230, 230, 230), thickness=10)
            
            out.write(annotated_frame)
    else:
        break

cap.release()
out.release()
cv2.destroyAllWindows()
