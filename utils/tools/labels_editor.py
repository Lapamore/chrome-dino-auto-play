import os

labels_new_dict = {
    '15' : '0',
    '16' : '1',
    '17' : '2'
}

files = [file for file in os.listdir('dataset/day/') if os.path.splitext(file)[-1] == '.txt']

for file_name in files[1:]:
    file_path = 'dataset/day/' + file_name
    with open(file_path, 'r') as file:
        lines = file.readlines()

    for i in range(len(lines)):
        line = lines[i].split()
        if line:
            line[0] =  labels_new_dict[line[0]]
            lines[i] = ' '.join(line) + '\n'
    
    with open(file_path, 'w') as file:
        file.writelines(lines)

print("Метки обновлены успешно.")
