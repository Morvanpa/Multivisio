from ultralytics import YOLO
import cv2
import random

class PlayerTracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.colors = {}


    def detect_frame(self, frame):
        results = self.model.track(frame, persist=True, verbose=False)
        id_name_dict = results[0].names
        player_dict = {}
        suitcase_dict = {}
        for box in results[0].boxes:
            if box.id:
                track_id = int(box.id.tolist()[0]) #Pourquoi on peut avoir une bbox sans ID ??
                result = box.xyxy.tolist()[0]

                object_cls_id = box.cls.tolist()[0]
                object_cls_name = id_name_dict[object_cls_id]
                if object_cls_name == 'person' :
                    if track_id not in self.colors:
                        self.colors[track_id] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                    color = self.colors[track_id]
                    player_dict[track_id] = {'bbox': result, 'color': color} #Quel intérêt de mettre un dico dans un dico ? Autant mettre une liste non ? C'est juste plus visuel à la limite...
        return player_dict



