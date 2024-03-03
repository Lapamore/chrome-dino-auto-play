import cv2
from ultralytics import YOLO
import os

if not os.path.isdir('dataset/'):
    os.makedirs('dataset/images/')
    os.makedirs('dataset/labels/')

model = YOLO('darknet/best.pt')
video = cv2.VideoCapture('PATH_TO_VIDEO')
os.chdir("dataset/") 
index = 1 

while video.isOpened():
    success, frame = video.read()
    if not success:
        break

    frame = cv2.resize(frame, (frame.shape[1] // 4, frame.shape[0] // 4))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image_height, image_width, _ = frame.shape

    if index % 2 == 0:
        detection = model(frame) 
        box = detection[0]
        box = box.cpu()
        boxes = box.boxes
        cls_ = list(map(int, boxes.cls.tolist()))
        xyxy = boxes.xywhn.tolist()

        lines = [f"{cls_[index_box]} {' '.join(map(str, box_))}" for index_box, box_ in enumerate(xyxy)]

        with open(f'labels/dino_generate_day_{index}.txt', 'w') as file:
            for line in lines:
                print(line, file=file)
        
        filename = f'images/dino_generate_day_{index}.jpg'
        cv2.imwrite(filename, frame)
        print('Image {} save!'.format(index))

    index += 1

video.release()
cv2.destroyAllWindows()
