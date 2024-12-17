import cv2 as cv

class Display():
    cv.namedWindow("output", cv.WINDOW_NORMAL)  # Create scalable window for all displays to share

    def __init__(self,camera):
        self.image = camera
        if not self.image.isOpened():
            print("Camera initialization failed")
        self.window = "output" # Needs to be changed !!

    def display(self,frame):
        """ 
        Adds the specified bounding boxes and other things (?) to the frame and displays it
        """
        cv.imshow("Display",frame)