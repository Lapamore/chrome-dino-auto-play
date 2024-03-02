import cv2
import pyautogui
import keyboard
import mss
import mss.tools
from time import time
from keyboard_control import KeyboardController
import numpy as np
import logging
import threading
from threading import Event
from multiprocessing import Queue
from model import Model

logging.getLogger().setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logging.getLogger().addHandler(stream_handler)

queue_size = 10
q = Queue(maxsize=queue_size)
kb = KeyboardController()
model = Model("darknet/best_nano.pt").load_model()
barrier = threading.Barrier(2)
grab_running = Event()
image_processing_running = True



def stop_program():
    global grab_running, image_processing_running
    grab_running.set()
    image_processing_running = False


def image_processing(queue):
    global image_processing_running
    barrier.wait()

    loop_time = time()
    last_jump_time = time()
    start_time = time()
    jump_distance_max = 85
    min_distance_max = 30
    start_flag = False

    while image_processing_running:
        # Start proggram!
        if (
            (time() - loop_time) != 0
            and (round(1 / (time() - loop_time)) > 28)
            and (not start_flag)
        ):
            start_flag = True
            continue

        else:
            if queue.empty():
                continue

            screenshot = queue.get()
            result = model(screenshot, verbose=False)

            elapsed_time_since_jump = time() - last_jump_time

            if (
                elapsed_time_since_jump >= 16
                and jump_distance_max <= 230
                and min_distance_max <= 50
            ):
                jump_distance_max += 10
                min_distance_max += 2
                last_jump_time = time()

            for detection in result:
                detection = detection.cpu()
                boxes = detection.boxes
                idx = np.where(np.array(boxes.conf) > 0.8)
                xyxy = np.array(boxes.xyxy[idx])

                for k in xyxy:
                    x, y, x2, y2 = k
                    cv2.rectangle(
                        screenshot, (int(x), int(y)), (int(x2), int(y2)), (0, 255, 0), 2
                    )

                if len(xyxy) >= 2:
                    flag = False
                    xyxy_ = xyxy.copy()
                    cls_ = np.array(boxes.cls)
                    if (0 in cls_) and (np.count_nonzero(cls_ == 0) == 1):
                        try:
                            dino_index = np.where(cls_ == 0)[0].item()
                            dino_x, dino_y = int(xyxy[dino_index][2]), int(
                                xyxy[dino_index][1]
                            )
                        except Exception:
                            print("Индекс динозавра не может быть определен!")
                            continue

                        xyxy_ = np.delete(xyxy_, dino_index, axis=0)
                        cls_ = np.delete(cls_, dino_index, axis=0)

                        recognized_object_x = int(min(xyxy_[:, 0]))
                        min_index = np.argmin(xyxy_[:, 0])
                        recognized_object_y = int(xyxy_[min_index, 1])
                        recognized_object_y_2 = int(xyxy_[min_index, 3])

                        if dino_y >= 174:
                            # logging.info(f"{recognized_object_x} - {dino_x} = {recognized_object_x - dino_x}")
                            if 2 in cls_:
                                try:
                                    bird_index = np.where(cls_ == 2)[0].item()
                                    bird = xyxy_[bird_index]
                                    bird_y_min, bird_y = int(bird[1]), int(bird[3])
                                    if (
                                        int(bird[0]) == recognized_object_x
                                        and int(bird[1]) == recognized_object_y
                                    ):
                                        if (dino_y) <= bird_y - 10 and dino_y in range(
                                            bird_y_min, bird_y + 1
                                        ):
                                            if (recognized_object_x - dino_x) < 150:
                                                kb.crouch(0.4)
                                                flag = True
                                                logging.info(
                                                    "Динозавр спустился при виде птицы"
                                                )
                                except:
                                    continue

                            if abs(dino_y - recognized_object_y_2) > 7 and not flag:
                                distance = recognized_object_x - dino_x
                                if (
                                    distance < jump_distance_max
                                    and distance >= min_distance_max
                                ):
                                    if time() - start_time <= 50:
                                        kb.jump()
                                    else:
                                        kb.jump_and_crouch()

                                    logging.info("Динозавр совершил прыжок")

                                cv2.line(
                                    screenshot,
                                    (dino_x, dino_y),
                                    (recognized_object_x, dino_y),
                                    (0, 0, 255),
                                    3,
                                )

                            cv2.putText(
                                screenshot,
                                str(recognized_object_x - dino_x),
                                (200, 100),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,
                                (0, 255, 0),
                                2,
                            )

        cv2.putText(
            screenshot,
            str(round(1 / (time() - loop_time))),
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

        cv2.imshow("CV", screenshot)
        loop_time = time()

        key = cv2.waitKey(1)
        if key == 27:
            break

    cv2.destroyAllWindows()


def grab(queue):
    global grab_running
    barrier.wait()

    w, h = pyautogui.size()
    monitor = {"top": 0, "left": 0, "width": w, "height": h}

    with mss.mss() as sct:
        while not grab_running.is_set():
            if queue.full():
                continue

            img = sct.grab(monitor)
            img = np.array(img)
            img = img[:, :, :3]
            screenshot = cv2.resize(img, (576, 324))
            queue.put(screenshot)


if __name__ == "__main__":
    logging.info("Запуск основной программы")

    t1 = threading.Thread(target=grab, args=(q,))
    t2 = threading.Thread(target=image_processing, args=(q,))

    t1.start()
    t2.start()

    keyboard.add_hotkey("q", stop_program)

    t1.join()
    t2.join()

    while not q.empty():
        q.get()

    logging.info("Работа завершена")
