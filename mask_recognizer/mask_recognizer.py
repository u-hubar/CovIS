import cv2
import torch
import numpy as np

DEBUG = False


def load_model(path: str, idx: int = 0):
    model = torch.hub.load('ultralytics/yolov5',
                           'custom',
                           path=path)
    return model


def mask_recognition(model, image):
    img = np.copy(image)
    result = model(image)
    for row in result.pandas().xyxy[0].iterrows():
        if row[1]['name'] == 'with_mask':
            color = (0, 255, 0)
        elif row[1]['name'] == 'without_mask':
            color = (255, 0, 0)
        elif row[1]['name'] == 'mask_weared_incorrec':
            color = (255, 255, 0)
        else:
            color = (100, 100, 100)

        cv2.rectangle(img,
                      (int(row[1]['xmin']), int(row[1]['ymin'])),
                      (int(row[1]['xmax']), int(row[1]['ymax'])),
                      color,
                      2)

        if DEBUG:
            cv2.putText(img,
                        row[1]['name'],
                        (int(row[1]['xmax']) + 10, int(row[1]['ymax'])),
                        0,
                        0.3,
                        (125, 50, 30))

    return img[:, :, ::-1]
