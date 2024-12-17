from ultralytics import YOLO
import cv2 as cv
import display
import threading
from enum import Enum
import lienPersonSuitcase
import numpy as np

class State(Enum):
    WAITING = 0
    PROCESSING = 1
    DISPLAYING = 2
    TRACKING = 3

class Multivisio():
    
    def __init__(self, URLarray=["BusyAirport.mp4"],weights='weights/best.pt'):
        self.camlist = []
        self.camera_nb = len(self.camlist)
        self.model = YOLO(weights)
        self.alert = False
        self.display = []
        self.state = State.WAITING
        self.init_display()
        self.images =np.array(self.camera_nb) #TODO : Change this to an empty list of images (ndarray types)
        for i in range(self.camera_nb):
            self.camlist.append(cv.VideoCapture(URLarray[i]))
            if not self.camlist[i].isOpened():
                print("Error : The camera number %d couldn't be accessed",i)

        

    def seekLostBagage(self, cam_number):
        while True:
            #Wait for the condition to signal that the processing can start
            with cond:
                cond.wait_for(lambda: self.state == State.PROCESSING)
            # Process the next image
            ret, frame = self.camlist[cam_number].read()
            #Todo : Modify the lienPersonSuitcase.py to take in the frame and return the frame + bounding boxes and a boolean indicating if a suitcase is lost
            # If problem, start the tracking phase
            if self.alert == 1:
                self.state = State.TRACKING
                self.alert = 0
    

    def init_display(self):
        """
        Initializes the displays for all cameras, which will use the cv2 cam object to display the video streams
        """
        for n in range(self.camera_nb):
            self.display.append(display.Display(self.URLarray[n],self.camlist[n]))
        return 0

if __name__ == "__main__":
    mv = Multivisio()
    exit = False
    threads = []
    lock = threading.Lock()
    cond = threading.Condition()
    for i in range(mv.camera_nb):
        threads[i] = threading.Thread(target=mv.seekLostBagage, args=i)
        threads[i].start()
    while not exit: #TODO : Add a way to exit the loop when pressing a key or things like that
        
        
        # Wait for the children to process, then display the results TODO: Children and parent should be synchronized when processing/diplaying -> semaphore
        with cond:
            cond.wait_for(lambda: mv.state == State.DISPLAYING)
        for d in mv.display:
            d.display()


