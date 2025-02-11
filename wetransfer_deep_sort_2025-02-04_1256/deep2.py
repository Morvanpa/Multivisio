import cv2
import torch
import time
import numpy as np
from ultralytics import YOLO
from deep_sort.deep_sort import DeepSort


# Chemins vers les modèles
YOLO_MODEL = 'yolov10n.pt'
DEEP_SORT_WEIGHTS = 'wetransfer_deep_sort_2025-02-04_1256/deep_sort/deep/checkpoint/ckpt.t7'

# Initialisation du tracker DeepSORT
tracker = DeepSort(model_path=DEEP_SORT_WEIGHTS, max_age=100)

def main(video_path, skip_frames=5):
    # Initialisation de la vidéo
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Erreur : Impossible d'ouvrir la vidéo.")
        return

    # Propriétés de la vidéo
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Chargement du modèle YOLO
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    print(f"Utilisation de l'appareil : {device}")
    model = YOLO(YOLO_MODEL)

    # Suivi des ID uniques pour chaque classe
    unique_person_ids = set()
    unique_suitcase_ids = set()
    start_time = time.perf_counter()
    counter, fps_counter = 0, 0

    frame_index = 0  # Pour compter les frames

    # Boucle de traitement vidéo
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Fin de la vidéo.")
            break

        frame_index += 1
        if frame_index % skip_frames != 0:  # Sauter les frames pour améliorer les performances
            continue

        og_frame = frame.copy()

        # Détection avec YOLO
        results = model(frame, device=device, classes=[0, 28], conf=0.5, verbose=False)

        # Extraction des boîtes englobantes et confiances
        detections = []
        for result in results:
            for box in result.boxes.data.tolist():
                x1, y1, x2, y2, conf, cls_id = box
                w, h = int(x2 - x1), int(y2 - y1)
                x, y = int((x1+x2)/2), int((y1+y2)/2)
                detections.append(([x, y, w, h], float(conf), int(cls_id)))
        print(f"Détections : {detections}")

        # Préparation pour DeepSORT
        if len(detections) > 0:
            bboxes_xywh = np.array([det[0] for det in detections], dtype=float)
            confidences = np.array([det[1] for det in detections], dtype=float)
            classes = np.array([det[2] for det in detections], dtype=int)

            # Mise à jour du tracker
            tracks = tracker.update(bboxes_xywh, confidences, og_frame)
            # Affichage des résultats pour chaque track
            for track in tracks:
                if track[4] != -1:  # Vérification si le track est valide
                    track_id = track[4]
                    x1, y1, x2, y2 = map(int, track[:4])
                    cls_id = track[5] if len(track) > 5 else -1

                    # Déterminer la couleur et le label en fonction de la classe
                    if cls_id == 0:  # Personne
                        color = (0, 254, 0)
                        label = f"Person ID {track_id}"
                        unique_person_ids.add(track_id)
                    elif cls_id == 1:  # Valise
                        color = (0, 0, 255)
                        label = f"Suitcase ID {track_id}"
                        unique_suitcase_ids.add(track_id)
                    else:
                        color = (255, 255, 255)  # Par défaut
                        label = f"ID {track_id}"

                    # Dessiner la boîte englobante
                    cv2.rectangle(og_frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                    cv2.putText(og_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        else:
            print("Aucune détection pour ce frame.")

        # Affichage du nombre total de personnes et de valises suivies
        person_count = len(unique_person_ids)
        suitcase_count = len(unique_suitcase_ids)
        cv2.putText(og_frame, f"Person Count: {person_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(og_frame, f"Suitcase Count: {suitcase_count}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Calcul et affichage des FPS
        counter += 1
        elapsed_time = time.perf_counter() - start_time
        if elapsed_time > 1:
            fps_counter = counter / elapsed_time
            counter = 0
            start_time = time.perf_counter()

        cv2.putText(og_frame, f"FPS: {fps_counter:.2f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Enregistrement et affichage de la vidéo

        cv2.imshow("YOLOv10n + DeepSORT Tracking", og_frame)

        # Quitter avec 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Libération des ressources
    cap.release()

    cv2.destroyAllWindows()

if __name__ == "__main__":
    VIDEO_PATH = r'C:\Ensta\Tracking\input_videos\hall3.mp4'  # Chemin vers la vidéo d'entrée
    main(VIDEO_PATH)

