from ultralytics import YOLO

class Model:
    def __init__(self, path_to_model: str):
        """
        Инициализация объекта модели.

        Parameters:
            path_to_model (str): Путь к файлу модели YOLO.
        """
        self.path_to_model = path_to_model
    
    def load_model(self):
        """
        Загружает модель YOLO из указанного пути.

        Returns:
            YOLO: Объект модели YOLO.
        """
        model = YOLO(self.path_to_model)
        return model
