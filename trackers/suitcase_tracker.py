from ultralytics import YOLO
import pandas as pd
import cv2
import numpy as np

class SuitcaseTracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def interpolate_suitcase_position(self, suitcase_positions):
        suitcase_positions = [x.get(5, [np.nan, np.nan, np.nan, np.nan]) for x in suitcase_positions]        #convert the list into pandas dataframe
        df_suit_positions=pd.DataFrame(suitcase_positions, columns=['x1', 'y1', 'x2', 'y2'])
        #interpolate the missing values
        df_suit_positions = df_suit_positions.interpolate()
        df_suit_positions = df_suit_positions.bfill()
        df_suit_positions = df_suit_positions.fillna(0)
        #convert the dataframe into list
        suitcase_positions = [{5:x} for x in df_suit_positions.to_numpy().tolist()]
        return suitcase_positions

    def detect_frames_stream(self, frame):
        suitcase_detection = []
        suitcase_dict = self.detect_frame(frame)
        suitcase_detection.append(suitcase_dict)
        return suitcase_detection

    def detect_frame(self, frame):
        results = self.model.track(frame, persist=True, verbose=False)
        id_name_dict = results[0].names
        suitcase_dict = {}
        for box in results[0].boxes:
            track_id = int(box.id.tolist()[0])
            result = box.xyxy.tolist()[0]
            object_cls_id = box.cls.tolist()[0]
            object_cls_name = id_name_dict[object_cls_id]

            if object_cls_name == 'suitcase':
                suitcase_dict[track_id] = result
        return suitcase_dict

