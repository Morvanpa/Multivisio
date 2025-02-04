import cv2 as cv
import numpy as np

class Display():
    cv.namedWindow("Display", cv.WINDOW_NORMAL)  # Create scalable window for all displays to share
    def __init__(self):
        self.lastFrame = None

    def display(self,frames):
        """ 
        Adds the specified bounding boxes and other things (?) to the frame and displays it
        """
        frames = self.scale_images(frames)
        full_frame = np.concatenate(frames,axis=0)
        self.lastFrame = full_frame
        cv.imshow("Display",full_frame)
        cv.waitKey(50)
    
    def scale_images(self,frames):
        desired_size = frames[0].shape[0],frames[0].shape[1]
        for i in range(1,len(frames)):
            f = frames[i]
            frames[i] = cv.resize(f, (desired_size[1],desired_size[0]))
        return frames
if __name__ == "__main__":
    display = Display()
    video = cv.VideoCapture("BusyAirport.mp4")
    if (video.isOpened() == False):
        print("Error opening the video file")
    else:
        while video.isOpened():
            ret, frame = video.read()
            if ret == True:
                display.display(frame)
            else:
                print("Error")
        video.release()
        cv.destroyAllWindows()