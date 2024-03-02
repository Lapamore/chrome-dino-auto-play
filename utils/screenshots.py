import cv2
import os

video = cv2.VideoCapture('videos/gameplay_day.mp4')

if not os.path.isdir('dataset/'):
    os.makedirs('dataset/day/')
    os.makedirs('dataset/night/')

path_to_save = 'dataset/day/'
os.chdir(path_to_save) 
index = 1

while True:
    success, frame = video.read()
    if not success:
        print('Error or video end!')
        break

    if index % 10 == 0:
        filename = f'dino_{index}.jpg'
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (frame.shape[1] // 4, frame.shape[0] // 4))
        cv2.imwrite(filename, frame)
        print('Image {} save!'.format(index))
    index += 1
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
