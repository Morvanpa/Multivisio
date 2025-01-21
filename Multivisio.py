from ultralytics import YOLO
import cv2 as cv
import display
import threading
from enum import Enum
import lienPersonSuitcase
import numpy as np
import os

os.environ['YOLO_VERBOSE'] = 'False'
class State(Enum):
    WAITING = 0
    PROCESSING = 1
    DISPLAYING = 2
    TRACKING = 3



class Multivisio():
    
    def __init__(self, URLarray=["ValiseTest.mp4","ValiseTest.mp4"],weights='weights/best.pt'):
        self.camlist = []
        self.camera_nb = len(URLarray) #TODO : Parsing on the URLArray input...
        self.models = [YOLO(weights) for k in range(self.camera_nb)]
        self.display = []
        self.state = State.WAITING
        self.init_display()
        self.images =np.empty(self.camera_nb, dtype=np.ndarray)
        self.processingState = np.ones(self.camera_nb)
        for i in range(self.camera_nb):
            self.camlist.append(cv.VideoCapture(URLarray[i]))
            if not self.camlist[i].isOpened():
                print("Error : The camera number %d couldn't be accessed",i)
        print("Init OK")
        self.exit = False
        self.threads = []
        self.alertLock = threading.Lock()
        self.cond = threading.Condition()
        print("locks OK")
        for i in range(self.camera_nb):
            # Create threads without starting them
            self.threads.append(threading.Thread(target=self.seekLostBagage, args=[i]))
        self.threads.append(threading.Thread(target=self.bagageOwnerTracking))
        print("Threads Created")
        

    def launch(self):
        """
        This function allows the launching of the program
        """
        for i in range(len(self.threads)):
            # Start all threads
            self.threads[i].start()
        with self.cond:
            self.cond.wait_for(lambda: self.state == State.WAITING)
            # Take the conditionnal variable to change the state and wake up every thread
            self.state = State.PROCESSING
            self.cond.notify_all() 
            print("Launch : BEGINNING PROCESSING")
        self.show()
        return 0
        
        

    def show(self):
        """
        This function runs the main thread, which displays the images with the Display class in display.py
        This function uses two conditionnal locks to be able to display images while the next ones are being processed without problems
        """
        while not self.exit: #TODO : Add a way to exit the loop when pressing a key or things like that. Also, add a way to control how many frames are processed each second (a way to control the framerate)
            # Wait for the children to process, then display the results.
            with self.cond:
                self.cond.wait_for(lambda: self.state == State.DISPLAYING)
                # Critical section
                print("DISPLAYING")

                # Displaying the frames TODO : Verify that this works as it was just changed !!!!!
                for d in range(len(self.images)):
                    print(type(self.images[d]))
                    self.display[d].display(self.images[d])

                # Displaying finished -> Processing or Tracking
                self.processingState.fill(1)
                if self.alert == 1:
                    self.state = State.TRACKING
                else:
                    self.state = State.PROCESSING 
                print("END DISPLAYING")
                self.cond.notify_all()

                # End of Critical section
        return 0

    def seekLostBagage(self, cam_number):
        """
        This method runs on a thread and analyzes a camera to find abandonned luggage
        """
        print('I am thread %d'%cam_number)
        while True:
            #Wait for the condition to signal that the processing can start
            with self.cond:
                self.cond.wait_for(lambda: self.state == State.PROCESSING and self.processingState[cam_number] == 1)
            print("ID: %d - BEGIN PROCESSING"%cam_number)
            # Process the next image
            ret, frame = self.camlist[cam_number].read()
            if not ret:
                print("Error : Couldn't read the frame from camera number %d",cam_number)
            
            #TODO : Modify the lienPersonSuitcase.py to take in the frame and return the frame + bounding boxes and a boolean indicating if a suitcase is lost
            # PROCESSING
            processed_frame, alertFlag = lienPersonSuitcase.processFrame(frame,self.models[cam_number])
            print(type(processed_frame))

            # Updating the image with the new frame
            self.images[cam_number] = processed_frame
            print("ID: %d - UPDATED FRAME"%cam_number)

            # If problem, signal it. TODO : The tracking phase will be launched after the displaying
            if alertFlag == 1:
                with self.alertLock:
                    # Critical section
                    self.alert = 1 
                    print("ID: %d - Alert !"%cam_number)
                    # End of critical section
                
            # Signal that the processing is done; When the last thread is done processing, hand is given to the display thread
            with self.cond:
                # Critical section
                self.processingState[cam_number] = 0
                if self.nbpendingthreads() == 0:
                    self.state = State.DISPLAYING
                    print("ID: %d - Changed state to DISPLAYING"%cam_number)
                    self.cond.notify_all()
                # End of critical section
            print("ID: %d - END PROCESSING"%cam_number)

    def bagageOwnerTracking(self): #TODO : complete this function : What inputs, what outputs ? It has to change the self.alert when the tracking wants to be disabled
            while True: # TODO : Make a condition that allows to manually stop tracking/automatically stop if not found
                with self.cond: #Wait for the condition to signal that the tracking can start
                    # Critical section
                    self.cond.wait_for(lambda: self.state == State.TRACKING)
                    print("THEORETICALLY TRACKING")
                    # Here we would put the code for tracking 
                    # When Tracking is finished, begin everything again
                    self.state = State.DISPLAYING
                    self.alert = 0
                    self.cond.notify_all()
                    # End of Critical Section
                pass

    def init_display(self):
        """
        Initializes the displays for all cameras, which will use the cv2 cam object to display the video streams
        """
        for n in range(self.camera_nb):
            self.display.append(display.Display())
        print("INIT DISPLAY OK !")
        return 0
    
    

    def nbpendingthreads(self):
        """
        Returns the number of threads that are still processing an image
        """
        return sum(mv.processingState)

    

if __name__ == "__main__":
    mv = Multivisio()
    mv.launch()