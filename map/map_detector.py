import cv2
class MapDetector():
    def __init__(self):
        self.keypoints = []

    def add_keypoint(self, point):
        self.keypoints.append(point)

    def draw_keypoints(self, frame):
            for point in self.keypoints:
                cv2.circle(frame, point, 3, (255, 255, 255), -1)

