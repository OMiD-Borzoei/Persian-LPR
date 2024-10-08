import matplotlib

matplotlib.use('tkAGg')
from matplotlib import pyplot as plt
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
from time import sleep

names = ['1', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '2', '20', '21', '22', '23', '24', '25', '26',
         '27', '3', '4', '5', '6', '7', '8', '9']
classes = {
    11: 'ب',
    12: 'د',
    13: 'ع',
    14: '',
    15: 'ج',
    16: 'ق',
    17: 'ه',
    18: 'ل',
    19: 'م',
    20: '\u267F',  # Disabled People
    21: 'ن',
    22: 'س',
    23: 'ص',
    24: 'ت',
    25: 'ط',
    26: 'و',
    27: 'ی',
}
for class_id in range(1, 11):
    classes[class_id] = str(class_id - 1)

abs_path = 'D:/Uni/Term 7/Computer Vision/Project_V2/First Model/'
check_point = abs_path + 'runs/detect/train4/weights/best.pt'

character_recognizer_abs_path = 'D:/Uni/Term 7/Computer Vision/Project_V2/Character Recognizer/'
character_recognizer_best_parameters = character_recognizer_abs_path + 'runs/detect/train4/weights/best.pt'

licence_plate_recognizer_abs_path = 'D:/Uni/Term 7/Computer Vision/Project_V2/License Plate Recognizer/'
licence_plate_recognizer_best_parameters = licence_plate_recognizer_abs_path + 'runs/detect/train4/weights/best.pt'

ocr_model = YOLO(character_recognizer_best_parameters)
lpr_model = YOLO(licence_plate_recognizer_best_parameters)

lpr_size = (512, 512)
ocr_size = (416, 416)


def filter_overlapping_boxes(all_boxes, threshold=0.5):
    """
    Filter out overlapping boxes based on the area of intersection relative to the area of the smaller box.
    """
    boxes = all_boxes.xyxy
    indices = []
    removed = []
    for i in range(len(boxes)):
        flag = False
        for j in range(i + 1, len(boxes)):
            box1 = boxes[i]
            box2 = boxes[j]

            # Calculate intersection coordinates
            x_intersection = max(box1[0], box2[0])
            y_intersection = max(box1[1], box2[1])
            w_intersection = min(box1[2], box2[2]) - x_intersection
            h_intersection = min(box1[3], box2[3]) - y_intersection

            # Calculate areas
            area_intersection = max(0, w_intersection) * max(0, h_intersection)
            area_box1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
            area_box2 = (box2[2] - box2[0]) * (box2[3] - box2[1])

            # Calculate intersection over smaller box area
            iou = area_intersection / min(area_box1, area_box2)
            # print(iou)
            if iou > threshold:
                # print(iou, i, j)
                flag = True
                # Boxes are too close or overlapping, discard the one with lower confidence

                if all_boxes[i].conf > all_boxes[j].conf:
                    if i not in indices:
                        indices.append(i)
                        removed.append(j)
                else:
                    if j not in indices:
                        indices.append(j)
                        removed.append(i)
        if not flag:
            if i not in indices:
                indices.append(i)
    # print(indices)
    # print(removed)
    filtered_boxes = [all_boxes[i] for i in indices if i not in removed]
    return filtered_boxes

pathhhh = 'images/193.png'
pathh = 'images/valid/car-14-_jpg.rf.c74057e5f95279870fb8db4543ce235c.jpg'
def get_licence_plate(img=None, path=pathh):
    if img is not None:
        image = img
    else:
        image = cv2.imread(path)

    image = cv2.resize(image, lpr_size)

    results = lpr_model.predict(image)
    result = results[0]

    if len(result.boxes) == 0:
        print('No Licence Plate Found')

    elif len(result.boxes) > 1:
        print('More Than One License Plate Was Found')
        """
        To Do
        """

    else:

        lp = result.boxes
        print(f'Licence Plate Found with {lp.conf[0] * 100 :.2f} % Confidence')
        x1, y1, x2, y2 = [int(x) for x in lp.xyxy[0]]

        lp_image = image[y1:y2, x1:x2]
        lp_image = cv2.resize(lp_image, ocr_size)

        ocr_results = ocr_model.predict(lp_image)
        # Show the results

        # sleep(5)
        print('\n')
        ocr_result = ocr_results[0]


        print(len(ocr_result))
        filtered_boxes = filter_overlapping_boxes(ocr_result.boxes)
        print(len(filtered_boxes))
        xs = [int(box.xywh[0][0]) for box in filtered_boxes]
        # xs = [int(xywh[0]) for xywh in ocr_result.boxes.xywh]
        idxs = np.argsort(xs)
        lp_str = []
        for i in idxs:
            cls = int(ocr_result.boxes.cls[i])
            clas = int(names[cls])
            lp_str.append(classes[clas])

        print('\t\t---License Plate---\t\t')
        for i in lp_str:
            print(i)

        # plot a RGB numpy array of predictions
        return lp_str, result.plot(), ocr_result.plot()


if __name__ == "__main__":
    get_licence_plate()
