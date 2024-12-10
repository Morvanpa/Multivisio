import cv2 as cv
from time import localtime, strftime, time as t
import numpy as np

#Define constants for the program
framerate = 20
sizeX, sizeY= (320,240)
cut_time = 10 # En secondes
# Define the codec
fourcc = cv.VideoWriter_fourcc(*'MJPG')

def recup_infos():
    nb_cam = int(input("Renseignez le nombre de caméras : "))
    cap = np.empty(nb_cam,cv.VideoCapture)
    for i in range(nb_cam):
        ip = input("IP de la caméra n°"+str(i)+" = ")
        cap[i] = cv.VideoCapture("http://"+ip+":81/stream") # Pas de vérification que c'est bien une IP, mais bon pas trop grave
        print(cap[i].isOpened())
    return cap


def start_enregistrement(total_time=100,framerate=20,sizeX=320,sizeY=240,cut_time=10):
    cap = recup_infos()
    n = cap.size
    start_time = t()
    max_frame_number = cut_time*framerate
    stream_flag = True
    while stream_flag:
        if total_time != 0 and t() - start_time > total_time:
            break #To check wether the total time has passed or not. if total_time=0, the program never stops

        #Prepare the output file and the recording
        frameNumber = 0
        time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        name = "Camera{}__{}.avi"
        out = np.empty(n,dtype=cv.VideoWriter)
        for i in range(n):
            out[i] = cv.VideoWriter(name.format(i,time),fourcc,framerate,(sizeX,sizeY))
        
        #Start the recording
        while frameNumber < max_frame_number:
            for i in range(n):
                print(cap[i])
                ret, frame = cap[i].read()
                if not ret:
                    print("Can't receive frame (stream end?). Exiting ...")
                    stream_flag = False
                    break
                out[i].write(frame)
            if cv.waitKey(1) == ord('q'):
                stream_flag = False
                break
            frameNumber += 1

        #Save the recording
        for i in range(n):
            out[i].release()

    #Release capture at the end : 
    for i in range(n):
        cap[i].release()

if __name__ == "__main__":
    start_enregistrement()