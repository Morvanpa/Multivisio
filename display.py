import cv2 as cv

class Display():
    cv.namedWindow("output", cv.WINDOW_NORMAL)  # Create scalable window for all displays to share

    def __init__(self):
        self.lastFrame = None

    def display(self,frame):
        """ 
        Adds the specified bounding boxes and other things (?) to the frame and displays it
        """
        self.lastFrame = frame
        cv.imshow("Display",frame)