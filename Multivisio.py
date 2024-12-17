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
        self.camera_nb = len(URLarray) #TODO : Parsing on the URLArray input...
        self.model = YOLO(weights)
        self.display = []
        self.state = State.WAITING
        self.init_display()
        self.images =np.empty(self.camera_nb, dtype=np.ndarray) #TODO : Change this to an empty list of images (ndarray types)
        self.processingState = np.ones(self.camera_nb)
        for i in range(self.camera_nb):
            self.camlist.append(cv.VideoCapture(URLarray[i]))
            if not self.camlist[i].isOpened():
                print("Error : The camera number %d couldn't be accessed",i)
        print("Init OK !")

        

    def seekLostBagage(self, cam_number):
        print('I am a thread')
        while True:
            #Wait for the condition to signal that the processing can start
            with cond:
                cond.wait_for(lambda: self.state == State.PROCESSING)
            print("BEGIN PROCESSING")
            # Process the next image
            ret, frame = self.camlist[cam_number].read()
            self.images[cam_number] = frame
            if not ret:
                print("Error : Couldn't read the frame from camera number %d",cam_number)
            #TODO : Modify the lienPersonSuitcase.py to take in the frame and return the frame + bounding boxes and a boolean indicating if a suitcase is lost
            self.images[cam_number], alertFlag = lienPersonSuitcase.processFrame(frame,self.model)

            # If problem, start the tracking phase
            if alertFlag == 1: 
                with cond:
                    self.state = State.TRACKING
                    cond.notify_all()
            #Signify that the processing is done; When the last thread is done processing, hand is given to the display thread
            else:
                lock.acquire()
                self.processingState[cam_number] = 0
                if self.nbpendingthreads() == 0:
                    self.state = State.DISPLAYING
                    cond.notify_all()
                lock.release()
            print("END PROCESSING")

            
            
    

    def init_display(self):
        """
        Initializes the displays for all cameras, which will use the cv2 cam object to display the video streams
        """
        for n in range(self.camera_nb):
            self.display.append(display.Display())
        print("INIT DISPLAY OK !")
        return 0
    
    def bagageOwnerTracking(self): #TODO : complete this function : What inputs, what outputs ?
        while True:
            with cond: #Wait for the condition to signal that the tracking can start
                cond.wait_for(lambda: self.state == State.TRACKING)
            pass

    def nbpendingpthreads():
        """
        Returns the number of threads that are still processing an image
        """
        return sum(mv.processingState)

if __name__ == "__main__":
    mv = Multivisio()
    exit = False
    threads = []
    lock = threading.Lock()
    cond = threading.Condition()
    for i in range(mv.camera_nb):
        threads.append(threading.Thread(target=mv.seekLostBagage, args=[i]))
        threads[i].start()
    threads.append(threading.Thread(target=mv.bagageOwnerTracking))
    threads[-1].start()
    with cond:
        mv.state = State.PROCESSING
        cond.notify_all() 
    print("BEGIN PROCESSING; START OK")
    while not exit: #TODO : Add a way to exit the loop when pressing a key or things like that. Also, add a way to control how many frames are processed each second (a way to control the framerate)
        # Wait for the children to process, then display the results, while they begin calculating the next frame
        with cond:
            cond.wait_for(lambda: mv.state == State.DISPLAYING)
            print("BEGIN DISPLAYING")
            mv.processingState.fill(1) #Reset the processing states of every thread
            mv.state = State.PROCESSING
            cond.notify_all()
        for d in range(len(mv.display)):
            mv.display[d].display(mv.images[d])        

