from trackers import PlayerTracker
import show_methods
import cv2

def main():
    input_video_path = 'input_videos/air.mp4'

    #show
    show_methods.IdPersonn(input_video_path, fpsDivider=1, videoScale=0.25)


if __name__ == '__main__':
    main()