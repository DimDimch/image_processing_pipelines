import collections
import json
import os
import sqlite3 as db
from template_enums import templates_enums
import re


class CVLibGenerator:
    def __init__(self, files_ru: tuple, files_en: tuple):
        self.files_ru = files_ru
        self.files_en = files_en

        self.db_name = 'cvLib.db'
        self.ru_table_name = 'OperatorsRU'
        self.en_table_name = 'OperatorsEN'
        self.help_table_name = 'OperatorsMeta'
        self.connection = db.connect('data/' + self.db_name)

        self.lib_file_name = 'cvlib.py'
        self.prostack_path = r'"C:\ProStack\bin\prostak.exe"'
        self.image_magick_path = r'"C:\Program Files\ImageMagick\magick.exe"'

        if not os.path.exists('/files'):
            os.makedirs('/files')

    def run(self):
        # создаем базу данных
        self.create_table(self.files_ru, self.ru_table_name)
        self.create_table(self.files_en, self.en_table_name)
        self.create_help_table()

        # генерируем библиотеку
        self.create_library()
        pass

    def create_table(self, ini_files: tuple, table_name: str):
        # подготавливаем поля таблицы и insert-запросы
        attributes, requests = [], []
        for file in ini_files:
            attributes += CVLibGenerator.get_attributes(file)
            requests += CVLibGenerator.get_requests(file)
        attributes = set(attributes)

        with self.connection as con:
            # создаем таблицу
            cur = con.cursor()
            cur.execute('DROP TABLE IF EXISTS ' + table_name)
            cur.execute('CREATE TABLE ' + table_name + ' (' + ', '.join(attributes) + ')')
            # заполняем таблицу
            for req in requests:
                req = req.replace('INTO Operators', 'INTO ' + table_name)
                cur.execute(req)

    def create_help_table(self):
        with self.connection as con:
            cur = con.cursor()
            cur.execute(f"DROP TABLE IF EXISTS {self.help_table_name}")
            cur.execute(f"CREATE TABLE {self.help_table_name}(func_name, param_template, param_names, param_types, param_defaults)")

    def write_function_to_lib(self, function_meta) -> str:
        params = self.preprocess_params(function_meta['name'], function_meta['params'])
        command = self.preprocess_command(function_meta['command'])
        message = self.preprocess_message(function_meta['message'])
        implementor_path = self.preprocess_implementor(function_meta['implementor'])
        input_files_count = self.find_files_count(function_meta['input_formats'])

        # потом прибавим это для каждого кейса
        temp = f"\n\toutputs = FilesList(func_name='{function_meta['name']}', " \
                  f"formats='{function_meta['output_formats']}')"
        # @ParallelCVLib()\n
        result = f"# {self.preprocess_message(message)}\n"

        if input_files_count == 0:  # если нет входных файлов
            result += f"def {function_meta['name']}({params[0][2:]}) -> FilesList:"
            result += temp
            result += f"\n\tcommand = {implementor_path} + '{command}' + {params[1]} + ' ' + outputs.get_command()"
        elif input_files_count == 1:  # если только один входной файл
            result += f"def {function_meta['name']}(input: File{params[0]}) -> FilesList:" \
                      f"\n\tif input.format != '{function_meta['input_formats']}':" \
                      f"\n\t\tprint('ERROR in {function_meta['name']} function: incorrect type of input files')" \
                      f"\n\t\treturn FilesList()"
            result += temp
            result += f"\n\tcommand = {implementor_path} + '{command}' + {params[1]} + input.file_path + ' ' + outputs.get_command()"
        else:  # если больше одного входного файла
            result += f"def {function_meta['name']}(inputs: FilesList{params[0]}) -> FilesList:" \
                      f"\n\tif not inputs.check_formats('{function_meta['input_formats']}'):" \
                      f"\n\t\tprint('ERROR in {function_meta['name']} function: incorrect type of input files')" \
                      f"\n\t\treturn FilesList()"
            result += temp
            if function_meta['need_comma'] == 1:  # если нужна запятая (по умолчанию)
                result += f"\n\tcommand = {implementor_path} + " + f"'{command}' + {params[1]} + " \
                          f"inputs.get_command() + ' ' + outputs.get_command()"
            else:
                result += f"\n\tcommand = {implementor_path} + " + f"'{command}' + {params[1]} + " \
                          f"inputs.get_command(need_comma=False) + ' ' + outputs.get_command()"

        result += f"\n\tos.system(command)" + \
                  f"\n\treturn outputs\n\n\n"
        return result

    def create_library(self):
        with self.connection as con:
            cur = con.cursor()
            cur.execute(
                "SELECT name, uidescription, inputs, outputs, message, executable, type, implementor FROM " + self.en_table_name)
            rows = cur.fetchall()

        with open(self.lib_file_name, encoding='utf-8', mode='w') as file:
            result = f"import os\n" \
                     f"from files_manager import File, FilesList\n" \
                     f"from cvlib_enums import *\n\n" \
                     f"prostack_path = r'{self.prostack_path}'\n" \
                     f"image_magick_path = r'{self.image_magick_path}'\n\n\n"
            for row in rows:
                named_row = {
                    'name': row[0],
                    'params': row[1],
                    'input_formats': row[2],
                    'output_formats': row[3],
                    'message': row[4],
                    'command': row[5],
                    'need_comma': row[6],
                    'implementor': row[7]
                }
                result += self.write_function_to_lib(named_row)
            file.write(result)

    @staticmethod
    def get_attributes(file_name) -> []:
        list_pole = []
        with open(file_name, encoding='utf-8', mode='r') as file:
            all_file = file.readlines()
            for line in all_file:
                s1 = "Operators ("
                s2 = ") VALUES"

                if 'INSERT OR REPLACE INTO Operators' in line:
                    first = line.index(s1) + len(s1)
                    last = line.index(s2)
                    list_p = line[first:last].split(", ")
                    p = list(map(lambda pole: list_pole.append(pole), list_p))
        return list_pole

    @staticmethod
    def get_requests(file_name) -> []:
        with open(file_name, encoding='utf-8', mode='r') as file:
            file_string = file.read()

        pattern = "INSERT"
        x = file_string.split(pattern)
        list_sql_filter = list(filter(lambda str: "Operators" in str, x))
        list_sql_result = list(map(lambda str: pattern + " " + str, list_sql_filter))

        return list_sql_result

    @staticmethod
    def preprocess_message(message: str) -> str:
        # отбрасываем все после точки
        result = message.split('.', 1)[0]

        # удаляем перевод строки, если он в середине сообщения или в конце
        if result.find('\n') != -1:
            result = result.replace('\n', ' ')
            if result.endswith(' '):
                result = result[:-1]

        # убираем "Этот оператор" или "This operator"
        if result.startswith('Этот оператор') or result.startswith('This operator') \
                or result.startswith('этот оператор') or result.startswith('this operator'):
            result = result[len('Этот оператор '):]

        # первую букву в нижний регистр
        result = result[:1].lower() + result[1:]

        return result

    def preprocess_params(self, func_name: str, params: str) -> ():
        if params == 'N/A' or params == '':
            return '', "' '"

        def preprocess_param_type(t: str) -> str:
            if t == 'double':
                return 'float'
            if t == 'string':
                return 'str'
            if t == 'bool':
                return 'str'
            return t

        def preprocess_param_name(name: str) -> str:
            result = (name
                      .replace(' ', '_')
                      .replace("'", '')
                      .replace(".", '')
                      .replace("?", ''))
            result = result.lower()

            if result == 'lambda':
                result = 'lmbd'
            if result.find('(') != -1:
                result = result[:result.find('(')]
            return result

        def crate_enum(enum_values: [], param_name: str) -> (str, str, str):
            # проверяем, есть ли такой набор значений в шаблонных enums, если да - возвращаем шаблон
            for template_values in templates_enums:
                if collections.Counter(enum_values) == collections.Counter(template_values):
                    return templates_enums[template_values]['name'], templates_enums[template_values]['default_value']

            # если среди шаблонов не нашлось, то делаем новый и добавляем
            enum_name = func_name.capitalize() + param_name.capitalize() + 'Enum'
            body = f"class {enum_name}(str, Enum):\n"
            for e in enum_values:
                if re.search(r'\d', e):
                    print(f"ERROR: проблема в формировании enum для функции {func_name} из-за наличия чисел")
                else:
                    body += f"    {e.upper()} = '{e}'\n"

            enum_values = tuple(enum_values)
            templates_enums[enum_values] = {
                'name': enum_name,
                'default_value': enum_values[0],
                'body': body + '\n\n'
            }

            return templates_enums[enum_values]['name'], templates_enums[enum_values]['default_value']

        items = params.split('\n')
        # убираем двоеточие в конце
        for i in range(len(items)):
            items[i] = items[i].strip()[:-1]

        # получаем кол-во параметров для функции
        count = int(items[0])

        # парсим параметры функции
        param_names = []
        param_types = []
        default_values = []
        for i in range(1, count + 1):
            # разбиваем по двоеточию
            a = items[i].split(';')

            default_values.append(a[-1])  # последнее пусть всегда будет дефолтное значение, даже для choice
            normal_param_name = preprocess_param_name(a[0])
            param_names.append(normal_param_name)  # первое это всегда имя параметра
            if a[1] == 'choice':  # если choice, надо сделать enum
                enum_name, default_value = crate_enum(enum_values=a[3:], param_name=normal_param_name)

                param_types.append(enum_name)
                default_values[-1] = f"{enum_name}.{default_value.upper()}"
            else:
                param_types.append(preprocess_param_type(a[1]))

        # создаем строчку для простака
        prostack_command = "' " + items[-1]

        k = 0
        temp = ''
        while k < len(prostack_command):
            if prostack_command[k] == '$':
                if k + 2 < len(prostack_command) and re.search(r'\d', prostack_command[k + 2]):  # если двузначное число
                    n = int(prostack_command[k + 1:k + 3])
                    k += 3
                else:
                    n = int(prostack_command[k + 1])
                    k += 2

                if str(param_types[n - 1]).endswith('Enum'):
                    temp += "' + str(" + str(param_names[n - 1]) + ".value) + '"
                else:
                    temp += "' + str(" + str(param_names[n - 1]) + ") + '"
            else:
                temp += prostack_command[k]
                k += 1

        # убираем лишние символы в конце
        while temp[-1] == "'" or temp[-1] == ' ' or temp[-1] == '+':
            temp = temp[:-1]

        if temp[-1] != ')':  # значит последнее было не str(..) и нужно добавить "'"
            temp += "'"

        prostack_command = temp

        # создаем строчку для объявления функции
        func_command = ""
        for i in range(1, count + 1):
            if param_types[i - 1] == 'str':
                func_command += param_names[i - 1] + ": " + param_types[i - 1] + " = '" + default_values[i - 1] + "', "
            else:
                func_command += param_names[i - 1] + ": " + param_types[i - 1] + " = " + default_values[i - 1] + ", "
        func_command = func_command[:-2]  # убираем запятую и пробел

        # записываем все enum'ы в файл
        with open('cvlib_enums.py', 'w') as file:
            file.write('from enum import Enum\n\n\n')
            for val in templates_enums.values():
                file.write(val['body'])

        # добавляем в базу
        # поля: func_name, param_template, param_names, param_types, param_defaults
        with self.connection as con:
            cur = con.cursor()
            req = f'INSERT INTO {self.help_table_name} VALUES(' + \
                f"'{func_name}'," + \
                f"'{items[-1]}'," + \
                "'[\"{}\"]', ".format('", "'.join(param_names)) + \
                "'[\"{}\"]', ".format('", "'.join(param_types)) + \
                "'[\"{}\"]'".format('", "'.join(default_values)) + \
                ')'
            cur.execute(req)

        return ', ' + func_command, prostack_command + " + ' '"

    @staticmethod
    def preprocess_command(command: str) -> str:
        if command.startswith('prostak'):
            return command[len('prostak'):]
        else:
            return command

    @staticmethod
    def preprocess_implementor(implementor: str) -> str:
        if implementor == 'ProStack':
            return "prostack_path"
        elif implementor == 'IM':
            return "image_magick_path + ' '"

    @staticmethod
    def find_files_count(files: str) -> int:
        if files == '':
            return 0
        else:
            return len([f for f in files.split(',') if f != ''])
