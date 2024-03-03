import os

input_folder = 'dataset/night/'
output_folder = 'dataset/day_renamed/'

# Создаем новую папку для сохранения переименованных файлов
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Проходим по каждому файлу в папке
for file_name in os.listdir(input_folder):
    # Формируем пути к исходному и новому файлу
    file_path = os.path.join(input_folder, file_name)
    new_file_name = file_name.split('.')[0] + '_night.' + file_name.split('.')[-1]
    new_file_path = os.path.join(output_folder, new_file_name)

    # Переименовываем файл
    os.rename(file_path, new_file_path)

print("Файлы успешно переименованы.")