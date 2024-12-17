import numpy as np
from pandas.core.computation.expr import intersection
import cv2
import random
import itertools

def generate_random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return (r, g, b)

def get_center(bbox):
    x1, y1, x2, y2 = bbox
    cx=int((x1+x2)/2)
    cy=int(y2)
    return (cx, cy)

def get_distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return np.sqrt((x2-x1)**2 + (y2-y1)**2)

def draw_bboxes_stream(frame, track_id, bbox, color):
        x1, y1, x2, y2 = bbox
        cv2.putText(frame, f"ID: {track_id}", (int(bbox[0]), int(bbox[1])-10), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (255, 255, 255), 1)

        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)

def bbox_distance(bbox1, bbox2, threshold=0.2):
    c1=get_center(bbox1)
    c2=get_center(bbox2)
    distance = get_distance(c1, c2)
    return distance

def bbox_covering(bbox1, bbox2, threshold=0.05, type='center'):
    if type == 'intersection':
        x1, y1, x2, y2 = bbox1
        x3, y3, x4, y4 = bbox2

        # Ensure areas are positive
        area_bbox1 = abs(x2 - x1) * abs(y2 - y1)
        area_bbox2 = abs(x4 - x3) * abs(y4 - y3)

        # Area of the smaller box
        area = min(area_bbox1, area_bbox2)

        # Calculate the intersection rectangle
        xleft = max(x1, x3)
        xright = min(x2, x4)
        ytop = max(y1, y3)
        ybottom = min(y2, y4)
        if xright < xleft or ybottom < ytop:
            return False  # No intersection
        deltax = xright - xleft
        deltay = ybottom - ytop
        intersection = deltax * deltay
        # Check if the intersection covers enough of the smaller area
        if intersection > threshold * area:
            return True
        else:
            return False

    elif type == 'center':
        c1 = get_center(bbox1)
        c2 = get_center(bbox2)

        distance = get_distance(c1, c2)
        if distance > 0.5 * (bbox1[3] - bbox1[1]):
            return False
        else:
            return True
()

def valisePersonne(frame, player_detection, suitcase_detection):
    lien_dict={}
    for player_dict in player_detection:
        for suitcase_dict in suitcase_detection:
            for track_id2, bbox2 in suitcase_dict.items():
                for track_id, data in player_dict.items():
                    bbox = data['bbox']
                    color = data['color']
                    if bbox_covering(bbox, bbox2, type='intersection'):
                        lien_dict[track_id] = track_id2
                        draw_bboxes_stream(frame, track_id, bbox, color)
                        draw_bboxes_stream(frame, track_id2, bbox2, color)
                        cv2.line(frame, get_center(bbox), get_center(bbox2), color, 2)
                    elif track_id not in lien_dict and track_id2 not in lien_dict.values():
                        draw_bboxes_stream(frame, track_id, bbox, (255, 255, 255))
                        draw_bboxes_stream(frame, track_id2, bbox2, (255, 255, 255))
    return lien_dict


def valisePersonneDist(player_detection, suitcase_detection, frame):
    print("player_detection", player_detection)
    return False
