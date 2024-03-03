import logging.config

def setup_logging():
    """
    Настройка конфигурации логирования для программы.

    Создает конфигурацию логирования, включая форматирование и вывод в консоль.

    """
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '%(asctime)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
            },
        },
        'root': {
            'level': 'INFO',  # Уровень логирования INFO, можно изменить на DEBUG, WARNING, ERROR, и т.д.
            'handlers': ['console'],
        },
    })
