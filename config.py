from keyboard_control import KeyboardController
from model import Model
from time import time


class GameConfig:
    """
    Класс GameConfig содержит настройки и конфигурации для основной игровой программы.

    Attributes:
        QUEUE_SIZE (int): Максимальный размер очереди для обработанных изображений.
        JUMP_DISTANCE_MAX (int): Максимальное расстояние для прыжка динозавра.
        MIN_JUMP_DISTANCE (int): Минимальное расстояние для прыжка динозавра.
        FRAME_THRESHOLD (int): Пороговое значение кадров в секунду для определения старта программы.
        START_TIME (float): Время старта программы.
        START_FLAG (bool): Флаг, указывающий на начало программы.
        PATH_TO_MODEL (str): Путь к файлу модели для распознавания объектов.
        kb (KeyboardController): Экземпляр класса KeyboardController для управления клавиатурой.
        model (Model): Экземпляр класса Model для загрузки и использования модели YOLO.
    """
    QUEUE_SIZE = 10
    JUMP_DISTANCE_MAX = 85
    MIN_JUMP_DISTANCE = 30
    FRAME_THRESHOLD = 28
    START_TIME = time()
    START_FLAG = False
    PATH_TO_MODEL = "darknet/best_nano.pt"

    kb = KeyboardController()
    model = Model(PATH_TO_MODEL).load_model()