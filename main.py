import cv2
import pyautogui
import keyboard
import mss
import mss.tools
from time import time
import numpy as np
import logging
import threading
from utils.config import GameConfig
from threading import Event
import threading
from multiprocessing import Queue
from utils.keyboard_control import KeyboardController
from utils.log_config import setup_logging

# Логирование
setup_logging()

# Создание объекта класса конфигурации
config = GameConfig()
# Экземпляр класса KeyboardController для управления клавиатурой.
kb = KeyboardController()

barrier = threading.Barrier(2)
q = Queue(maxsize=config.QUEUE_SIZE)

is_grab_running = Event()
is_image_processing_running = True


# Функция остановки действия программы
def shutdown():
    global is_grab_running, is_image_processing_running
    is_grab_running.set()
    is_image_processing_running = False


# Основная функция обработки изображений
def image_processing(queue):
    global is_image_processing_running
    barrier.wait()

    loop_time = time()
    last_jump_time = time()

    jump_distance_max = config.JUMP_DISTANCE_MAX
    min_jump_distance = config.MIN_JUMP_DISTANCE
    start_flag = config.START_FLAG

    while is_image_processing_running:
        if (
            (time() - loop_time) != 0
            and (round(1 / (time() - loop_time)) > config.FRAME_THRESHOLD)
            and (not start_flag)
        ):
            start_flag = True
            logging.info("Программа работает, можете начинать игру!")
            continue

        else:
            if queue.empty():
                continue

            screenshot = queue.get()
            result = config.model(screenshot, verbose=False)
            elapsed_time_since_jump = time() - last_jump_time

            if (
                elapsed_time_since_jump >= 15
                and jump_distance_max <= 230
                and min_jump_distance <= 50
            ):
                jump_distance_max += 10
                min_jump_distance += 2
                last_jump_time = time()

            for detection in result:
                detection = detection.cpu()
                boxes = detection.boxes
                idx = np.where(np.array(boxes.conf) > config.CONFIDENCE_THRESHOLD)
                coordinates = np.array(boxes.xyxy[idx])

                for k in coordinates:
                    x, y, x2, y2 = k
                    cv2.rectangle(
                        screenshot, (int(x), int(y)), (int(x2), int(y2)), (0, 255, 0), 2
                    )

                if len(coordinates) >= 2:
                    is_crouch_performed = False
                    update_coordinates = coordinates.copy()
                    cls_ = np.array(boxes.cls)
                    if (0 in cls_) and (np.count_nonzero(cls_ == 0) == 1):
                        try:
                            dino_index = np.where(cls_ == 0)[0].item()
                            dino_x, dino_y = int(coordinates[dino_index][2]), int(
                                coordinates[dino_index][1]
                            )
                        except Exception:
                            # print("Индекс динозавра не может быть определен!")
                            continue

                        update_coordinates = np.delete(
                            update_coordinates, dino_index, axis=0
                        )
                        cls_ = np.delete(cls_, dino_index, axis=0)

                        recognized_object_x = int(min(update_coordinates[:, 0]))
                        min_index = np.argmin(update_coordinates[:, 0])
                        recognized_object_y = int(update_coordinates[min_index, 1])
                        recognized_object_y_2 = int(update_coordinates[min_index, 3])

                        if dino_y >= 174:
                            if 2 in cls_:
                                try:
                                    bird_index = np.where(cls_ == 2)[0].item()
                                    bird = update_coordinates[bird_index]
                                    bird_y_min, bird_y = int(bird[1]), int(bird[3])
                                    if (
                                        int(bird[0]) == recognized_object_x
                                        and int(bird[1]) == recognized_object_y
                                    ):
                                        if (dino_y) <= bird_y - 10 and dino_y in range(
                                            bird_y_min, bird_y + 1
                                        ):
                                            if (recognized_object_x - dino_x) < 150:
                                                kb.crouch()
                                                is_crouch_performed = True
                                except:
                                    continue

                            if (
                                abs(dino_y - recognized_object_y_2) > 7
                                and not is_crouch_performed
                            ):
                                distance = recognized_object_x - dino_x
                                if (
                                    distance < jump_distance_max
                                    and distance >= min_jump_distance
                                ):
                                    if time() - config.START_TIME <= 55:
                                        kb.jump()
                                    else:
                                        kb.jump_and_crouch()

                                cv2.line(
                                    screenshot,
                                    (dino_x, dino_y),
                                    (recognized_object_x, dino_y),
                                    (0, 0, 255),
                                    3,
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


# Функция захвата изображений и передачи в очередь
def grab(queue):
    global is_grab_running
    barrier.wait()

    w, h = pyautogui.size()
    monitor = {"top": 0, "left": 0, "width": w, "height": h}

    with mss.mss() as sct:
        while not is_grab_running.is_set():
            if queue.full():
                continue

            img = sct.grab(monitor)
            img = np.array(img)
            img = img[:, :, :3]
            screenshot = cv2.resize(img, (config.RESIZE_WIDTH, config.RESIZE_HEIGHT))
            queue.put(screenshot)


# Запуск основных процессов
if __name__ == "__main__":
    logging.info("Запуск основной программы")

    t1 = threading.Thread(target=grab, args=(q,))
    t2 = threading.Thread(target=image_processing, args=(q,))

    t1.start()
    t2.start()

    keyboard.add_hotkey("q", shutdown)

    t1.join()
    t2.join()

    while not q.empty():
        q.get()

    logging.info("Работа завершена")
