
from utils.model import Model
from time import time


class GameConfig:
    """
    Класс GameConfig содержит настройки и конфигурации для основной игровой программы.

    Attributes:
        QUEUE_SIZE (int): Максимальный размер очереди для обработанных изображений.
        CONFIDENCE_THRESHOLD (float): Минимальное значение уверенности, которое объект должен иметь, чтобы быть успешно обнаруженным моделью.
        JUMP_DISTANCE_MAX (int): Максимальное расстояние для прыжка динозавра.
        MIN_JUMP_DISTANCE (int): Минимальное расстояние для прыжка динозавра.
        FRAME_THRESHOLD (int): Пороговое значение кадров в секунду для определения старта программы.
        RESIZE_WIDTH (int): Ширина, на которую будет изменено входящее изображение.
        RESIZE_HEIGHT (int): Высота, на которую будет изменено входящее изображение.
        START_TIME (float): Время старта программы.
        START_FLAG (bool): Флаг, указывающий на начало программы.
        PATH_TO_MODEL (str): Путь к файлу модели для распознавания объектов.
        model (Model): Экземпляр класса Model для загрузки и использования модели YOLO.
    """
    QUEUE_SIZE = 10
    CONFIDENCE_THRESHOLD = 0.8
    JUMP_DISTANCE_MAX = 85
    MIN_JUMP_DISTANCE = 30
    FRAME_THRESHOLD = 28
    RESIZE_WIDTH = 576
    RESIZE_HEIGHT = 324
    START_TIME = time()
    START_FLAG = False
    PATH_TO_MODEL = "yolov8_model/best_nano.pt"

    model = Model(PATH_TO_MODEL).load_model()
