#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
from ultralytics import YOLO

# Chargement du modèle YOLOv10n
MODEL_PATH = '/home/shakib/Desktop/s3/multivision/result/20_epochsf2/weights/best.pt'
model = YOLO(MODEL_PATH)

def test_yolo_detections(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Erreur : Impossible d'ouvrir la vidéo.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Détection avec YOLOv10n
        results = model(frame, verbose=False)[0]

        # Affichage des détections
        print("Détections YOLO : ", results.boxes.data)  # Débogage : structure exacte des détections

        for det in results.boxes.data.tolist():  # Convertir en liste pour itération
            x1, y1, x2, y2, conf, cls_id = det
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            cls_id = int(cls_id)

            # Dessiner la boîte
            color = (0, 255, 0) if cls_id == 0 else (0, 0, 255)
            label = f"Classe: {cls_id}, Confiance: {conf:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        cv2.imshow("YOLOv10n Test", frame)

        # Quitter avec 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    VIDEO_PATH = '/home/shakib/Documents/GitHub/Multivisio/ValiseTest.mp4'
    test_yolo_detections(VIDEO_PATH)
