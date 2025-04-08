import cv2 as cv
import numpy as np



class Display():
    cv.namedWindow("Display", cv.WINDOW_NORMAL)  # Create scalable window for all displays to share
    def __init__(self,fps, camera_nb):
        self.displayFPS = fps
        self.processedFrames = [None for k in range(camera_nb)]
        

    

    def display(self,frames, imageInfo, minimaps):
        """ 
        Adds the specified bounding boxes and other things (?) to the frame and displays it
        """
        for k in range(len(frames)): #Add the squares, links, and minimap to the frame
            frame = frames[k]
            info = imageInfo[k][0] #Format : info[x] is info about the ID number x
            info_suitcases = imageInfo[k][1]
            info.update(info_suitcases) #Dangerous because we could lose information if a suitcase and a person have the same ID ! 
            processedFrame = self.squares(frame, info)
            processedFrame = self.link(processedFrame)
            processedFrame = self.map(processedFrame)
            minimaps[k].set_canvas_background_box_position(processedFrame)
            minimaps[k].set_mini_map_position()
            minimaps[k].set_map_drawing_key_points()
            minimaps[k].set_map_lines()
            processedFrame = minimaps[k].draw_map_key(processedFrame)
            processedFrame = minimaps[k].draw_map_lines(processedFrame)            
            processedFrame = minimaps[k].draw_background_rect(processedFrame)
            processedFrame = minimaps[k].draw_mini_map(processedFrame)
            self.processedFrames[k] = processedFrame
            
        self.processedFrames = self.scale_images(self.processedFrames) # Resize frames to match sizes
        full_frame = np.vstack(self.processedFrames) #concatenate frames in 1 big frame TODO : Make a different  function to concatenate everything in 1 image (App needs all images !)
        def mouse_callback(event, x, y, flags, param): # Calculates the coordinates on the picture when we click somewhere
            if event == cv.EVENT_LBUTTONDOWN:
                desired_size = self.processedFrames[0].shape[0]
                frame_nb = y // desired_size
                scaleFactor = desired_size/frames[frame_nb].shape[0]
                x_descaled = x * 1/scaleFactor
                y_descaled = (y%desired_size) * 1/scaleFactor
                print(full_frame.shape[0])
                
                print(f"Mouse position: ({x_descaled}, {y_descaled})")

        cv.setMouseCallback("Display",mouse_callback)
        cv.imshow("Display",full_frame)
        #cv.waitKey(int(1000/self.displayFPS)) TODO : Use this line when the program is capable of handling displaying and computing in parallel !
        cv.waitKey(1)
    
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
        desired_size = frames[0].shape[0]
        for i in range(1,len(frames)):
            f = frames[i]
            scaleFactor = 1/(desired_size/f.shape[0])
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