from ultralytics import YOLO
import pandas as pd
import cv2
import numpy as np

class SuitcaseTracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def interpolate_suitcase_position(self, suitcase_positions):
        # Extraire les positions pour la clé 5 de chaque frame
        frames = list(suitcase_positions.keys())
        positions = [suitcase_positions[frame][5] if isinstance(suitcase_positions[frame], dict) else [np.nan, np.nan, np.nan, np.nan] for frame in frames]

        # Créer un DataFrame à partir des positions
        df_positions = pd.DataFrame(positions, columns=['x1', 'y1', 'x2', 'y2'])

        # Interpoler les valeurs manquantes
        df_positions = df_positions.interpolate(method='linear')  # Interpolation linéaire
        df_positions = df_positions.bfill()  # Remplissage vers l'arrière
        df_positions = df_positions.fillna(0)  # Remplir tout reste avec 0

        # Reconstruire le dictionnaire avec les données interpolées
        for i, frame in enumerate(frames):
            suitcase_positions[frame][5] = df_positions.iloc[i].tolist()
        return suitcase_positions


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

