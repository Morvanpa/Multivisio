import numpy as np
from ultralytics import YOLO
import cv2
import time as t



def processFrame(frame, model):
    while True: #On peut l'enlever je pense ??
        suitcase = []
        person = []
        t0 = t.time()
        result = model.predict(frame,verbose=False)
        print("Prediction time : %d",t.time()-t0)
        for detection in result[0].boxes:
            xmin, ymin, xmax, ymax = detection.xyxy[0].cpu().numpy()
            confidence = detection.conf.cpu().numpy()
            label = detection.cls.cpu().numpy()  # Object class

            class_name = model.names[int(label)]
            if class_name == "person":
                person.append((int(xmin), int(ymin), int(xmax), int(ymax)))
                cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (255, 0, 0), 2)  # Blue for person

            if class_name == "suitcase":
                suitcase.append((int(xmin), int(ymin), int(xmax), int(ymax)))
                cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (0, 255, 0), 2)  # Green for suitcase
                
        flag = True #This flag is True when a suitcase is near a person (else False to detect lost suitcase) AS A FIRST APPROX
        # Proximity check between persons and suitcases
        for s in suitcase:
            deltaV = 80
            deltaH = 100

            for p in person:
                # Refine proximity check based on suitcase and person dimensions
                if ((s[3] <= p[3] + deltaV) and (s[3] >= p[3] - deltaV)) and ((s[0] <= p[2] + deltaH) and (s[2] >= p[0] - deltaH)):
                    
                    # Draw a line connecting the center of the suitcase and the person
                    cv2.line(frame, (s[0] + int(0.5 * (s[2] - s[0])), s[1] + int(0.5 * (s[3] - s[1]))),
                             (p[0] + int(0.5 * (p[2] - p[0])), p[1] + int(0.5 * (p[3] - p[1]))), (255, 0, 0), 5)
                    flag = True
                else:
                    cv2.imwrite("image.png", frame[p[1]:p[3], p[0]:p[2]] );
            if flag == False:
                print("Lost suitcase detected")
        return frame, flag #TODO : Return more precise things than juste flag, to be able to find the owner of a lost suitcase

        

    # Clean up resources
    cameraIP.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    url = 'http://172.20.10.12:81/stream'
    video = 'ValiseTest.mp4'
    model = YOLO('weights/best.pt')
    processFrame(video, model)