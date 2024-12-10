from ultralytics import YOLO
import cv2 as cv
import display
import threading

class Multivisio():
    
    def __init__(self, URLarray,weights='weights/best.pt'):
        self.camlist = []
        for i in range(self.camera_nb):
            self.camlist.append(cv.VideoCapture(URLarray[i]))
            if not self.camlist[i].isOpened():
                print("Error : The camera number %d couldn't be accessed",i)

        self.camera_nb = len(self.camlist)
        self.model = YOLO(weights)
        self.alert = False
        self.display = []
        self.init_display()

    def seekLostBagage(self, cam_number):
        while self.alert == False:
            pass
        return 0
    
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
    for i in range(mv.camera_nb):
        threads[i] = threading.Thread(target=mv.seekLostBagage, args=i)
    while not exit:
        
        # Check for lost bagages and do other necessary calculations
        mv.seekLostBagage()
        # Wait for the children to process, then display the results TODO: Children and parent should be synchronized when processing/diplaying -> semaphore
        for d in mv.display:
            d.display()


