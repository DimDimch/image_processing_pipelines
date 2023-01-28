import os
import random
import string
from typing import List, Dict


class FilesManager:
    def __init__(self, files_path: str = ''):
        self.files: List[str] = []
        if files_path != '':
            files = files_path.split(',')
            for file in files:
                if os.path.isfile(file):
                    self.files.append(file)
                else:
                    self.files.append('files/' + file)

        if not os.path.exists('/files'):
            os.makedirs('/files')

    def __add__(self, other):
        if isinstance(other, FilesManager):
            fm = FilesManager()
            fm.files += self.files + other.files
            return fm
        elif isinstance(other, str):
            self.files += other
            return self
        else:
            return NotImplemented

    def create_files(self, func_name: str, formats: str):
        formats = formats.split(',')
        for format in formats:
            file_name = self.generate_file_name(func_name, format)
            fp = open('files/' + file_name, 'w')
            fp.close()
            self.files.append('files/' + file_name)

    def get_command(self, file_types: str, need_comma: bool) -> str:
        result = ''
        file_types = file_types.split(',')
        for file_type in file_types:
            for file in self.files:
                if file.split('.')[-1] == file_type:
                    if need_comma:
                        result += file + ', '
                    else:
                        result += file + ' '
                    # self.files.remove(file)
        if need_comma:
            return result[:-2]
        else:
            return result[:-1]

    @staticmethod
    def generate_file_name(func_name: str, format: str) -> str:
        random_path = str(random.randint(0, 9)) + ''.join([random.choice(string.ascii_lowercase) for _ in range(5)])
        return func_name + '_output__' + random_path + '.' + format

    @staticmethod
    def clean_dir():
        files = os.listdir('files/')
        for f in files:
            os.remove('files/' + f)

