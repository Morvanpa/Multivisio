from ultralytics import YOLO
import cv2
import random
import cv2
import torch
import time
import numpy as np
from ultralytics import YOLO
from deep_sort.deep_sort import DeepSort
YOLO_MODEL = 'yolov10n.pt'
DEEP_SORT_WEIGHTS = 'wetransfer_deep_sort_2025-02-04_1256/deep_sort/deep/checkpoint/ckpt.t7'


class PlayerTracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.tracker = DeepSort(model_path=DEEP_SORT_WEIGHTS, max_age=100)
        self.colors = {}
        self.conf=[]
        self.bboxes_xywh = []


    def generate_color(self):
        return tuple(np.random.randint(0, 255, size=3).tolist())

    def detect_frameZ(self, frame):
        results = self.model.track(frame, persist=True, classes=[0], verbose=False)
        player_dict = {}

        for box in results[0].boxes:
            track_id = int(box.id.tolist()[0]) if box.id is not None else -1
            bbox = box.xyxy.tolist()[0]
            # Gestion des couleurs
            if track_id not in self.colors:
                self.colors[track_id] = self.generate_color()
            color = self.colors[track_id]

            player_dict[track_id] = {'bbox': bbox, 'color': color}

        return player_dict


    #deepsort
    def detect_frame(self, frame):
        results = self.model(frame, classes=[0], conf=0.5, verbose=False)
        detections = []


        for box in results[0].boxes.data.tolist():
            x1, y1, x2, y2, conf, cls_id = box
            w, h = int(x2 - x1), int(y2 - y1)
            x, y = int((x1 + x2) / 2), int((y1 + y2) / 2)
            detections.append(([x, y, w, h], float(conf), int(cls_id)))

        if detections:
            bboxes_xywh = np.array([det[0] for det in detections], dtype=float)
            confidences = np.array([det[1] for det in detections], dtype=float)
            tracks = self.tracker.update(bboxes_xywh, confidences, frame)
            player_dict = {}

            for track in tracks:
                track_id = int(track[4])
                x1, y1, x2, y2 = map(int, track[:4])
                cls_id = track[5] if len(track) > 5 else -1

                if track_id not in self.colors:
                    self.colors[track_id] = self.generate_color()
                color = self.colors[track_id]

                player_dict[track_id] = {
                    'bbox': [x1, y1, x2, y2],
                    'color': color,
                }

        else:
            player_dict = {}

        return player_dict
