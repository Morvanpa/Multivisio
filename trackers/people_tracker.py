from ultralytics import YOLO
import cv2
import random

class PlayerTracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.colors = {}

    def detect_frames_stream(self, frame):
        player_detection = []
        player_dict = self.detect_frame(frame)
        player_detection.append(player_dict)
        return player_detection

    def detect_frame(self, frame):
        results = self.model.track(frame, persist=True, verbose=False)
        id_name_dict = results[0].names
        player_dict = {}
        suitcase_dict = {}
        for box in results[0].boxes:
            track_id = int(box.id.tolist()[0])
            result = box.xyxy.tolist()[0]
            object_cls_id = box.cls.tolist()[0]
            object_cls_name = id_name_dict[object_cls_id]

            if object_cls_name == 'person' :
                if track_id not in self.colors:
                    self.colors[track_id] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                color = self.colors[track_id]
                player_dict[track_id] = {'bbox': result, 'color': color}

        return player_dict



