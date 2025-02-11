import cv2 as cv
import numpy as np

class Display():
    cv.namedWindow("Display", cv.WINDOW_NORMAL)  # Create scalable window for all displays to share
    def __init__(self):
        self.lastFrame = None

    def display(self,frames, imageInfo):
        """ 
        Adds the specified bounding boxes and other things (?) to the frame and displays it
        """
        
        for k in range(len(frames)): #Add the squares, links, and minimap to the frame
            frame = frames[k]
            info = imageInfo[k][0] #Format : info[x] is info about the ID number x
            info_suitcases = imageInfo[k][1]
            info.update(info_suitcases) #Dangerous because we could lose information if a suitcase and a person have the same ID ! 
            newFrame = self.squares(frame, info)
            newFrame = self.link(newFrame)
            newFrame = self.map(newFrame)

        frames = self.scale_images(frames) # Resize frames to match sizes
        full_frame = np.vstack(frames) #concatenate frames in 1 big frame
        self.lastFrame = full_frame
        cv.imshow("Display",full_frame)
        cv.waitKey(50)
    
    def squares(self, frame, info):
        for i in info.keys():
            bbox = info[i]['bbox']
            color = info[i]['color']
            cv.putText(frame, f"ID: {i}", (int(bbox[0]), int(bbox[1])-10), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))
            frame = cv.rectangle(frame, (int(bbox[0]),int(bbox[1])), (int(bbox[2]),int(bbox[3])), color, thickness=2)
        return frame

    def link(self, frame):
        return frame
    
    def map(self, frame):
        return frame

    def scale_images(self,frames):
        desired_size = frames[0].shape[1]
        for i in range(1,len(frames)):
            f = frames[i]
            scaleFactor = desired_size/f.shape[1]
            frames[i] = cv.resize(f, None, fx = scaleFactor, fy = scaleFactor)
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