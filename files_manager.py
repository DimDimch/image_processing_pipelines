import os
import random
import string
from typing import List
import shutil


def clean_dir():
    files = os.listdir(f"C:\\Users\\Дмитрий\\PycharmProjects\\automatic\\files\\")
    for f in files:
        os.remove(f"C:\\Users\\Дмитрий\\PycharmProjects\\automatic\\files\\{f}")


class File:
    def __init__(self, file_path: str = ''):
        self.files_storage = "C:\\results\\"

        # если есть пробелы и файл существует, то перемещаем его с новым названием без пробелов
        if ("%20" in file_path or " " in file_path) and os.path.isfile(file_path.replace("%20", " ")):
            new_path = file_path.split('\\')[-1].replace("%20", "_").replace(" ", "_").replace(",", "_")
            new_path = self.files_storage + new_path
            shutil.copy2(file_path.replace("%20", " "), new_path)
            self.file_path = new_path
        # если есть пробелы и файл новый
        elif "%20" in file_path or " " in file_path:
            new_path = file_path.split('\\')[-1].replace("%20", "_").replace(" ", "_").replace(",", "_")
            new_path = self.files_storage + new_path
            self.file_path = new_path
        # если нет пробелов и файл существует
        elif os.path.isfile(file_path):
            self.file_path = file_path
        # если файла не существует
        else:
            self.file_path = self.files_storage + file_path

        print(self.file_path)

        self.format = self.file_path.split('.')[-1]

    def __add__(self, other):
        if isinstance(other, File):
            fl = FilesList()
            fl.files.append(self)
            fl.files.append(other)
            return fl
        elif isinstance(other, FilesList):
            other.files.append(self)
            return other
        else:
            return NotImplemented


class FilesList:
    def __init__(self, func_name: str = '', formats: str = ''):
        self.files: List[File] = []

        if func_name != '' and formats != '':
            formats = formats.split(',')
            for f in formats:
                file_name = self.generate_file_name(func_name, f)
                # file_name = 'files/' + self.generate_file_name(func_name, f)
                self.files.append(File(file_name))

    def __add__(self, other):
        if isinstance(other, File):
            self.files.append(other)
            return self
        elif isinstance(other, FilesList):
            for item in other.files:
                self.files.append(item)
            return self
        else:
            return NotImplemented

    def __getitem__(self, item):
        return self.files[item - 1]

    def get_command(self, need_comma: bool = True) -> str:
        files = [fp.file_path for fp in self.files]
        if need_comma:
            return ','.join(files)
        else:
            return ' '.join(files)

    def check_formats(self, formats: str = '') -> bool:
        formats = [f for f in formats.split(',') if f != '']

        if len(formats) != len(self.files):
            return False

        for i in range(len(self.files)):
            if self.files[i].format != formats[i]:
                return False
        return True

    @staticmethod
    def generate_file_name(func_name: str, format: str) -> str:
        random_path = str(random.randint(0, 9)) + ''.join([random.choice(string.ascii_lowercase) for _ in range(5)])
        return func_name + '_output__' + random_path + '.' + format


EMPTY_LIST = FilesList()


def save_file(file: File, as_file: str):
    shutil.copy2(file.file_path, as_file)
