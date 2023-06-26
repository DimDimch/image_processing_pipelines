import json
import re
from typing import List
from ap_parser import Node
import sqlite3 as db
from template_enums import enums_numbers_to_str


class CVLibWriter:
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.name_generate_count = {'INS': -1, 'OUS': -1, 'PAM': -1}

        self.db_name = 'cvLib.db'
        self.help_table_name = 'OperatorsMeta'
        self.connection = db.connect('data/' + self.db_name)

        self.files_path = r'C:\Eyedisks\M1'

    def generate_var_name(self, node_type: str, starts_with: str = '', ends_with: str = '') -> str:
        def get_name(num, to_base=26, from_base=10):
            if isinstance(num, str):
                n = int(num, from_base)
            else:
                n = int(num)
            alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            if n < to_base:
                return alphabet[n]
            else:
                return get_name(n // to_base, to_base) + alphabet[n % to_base]

        self.name_generate_count[node_type] += 1
        return starts_with + get_name(self.name_generate_count[node_type]) + ends_with

    def change_file_path(self, file_path):
        return self.files_path + "\\" + file_path.split('/')[-1].replace("%20", " ")

    @staticmethod
    def get_in_nodes(node: Node):
        if node is None:
            return None
        else:
            if node.in_nodes is None:
                return None
            return [node.in_nodes[i + 1].num_node for i in range(len(node.in_nodes))]

    @staticmethod
    def get_out_nodes(node: Node):
        if node is None:
            return None
        else:
            if node.out_nodes is None:
                return None
            return [node.out_nodes[i + 1].num_node for i in range(len(node.out_nodes))]

    @staticmethod
    def find_template_match(template: str, value: str):
        a = 0
        b = 0
        result = {}
        while a < len(template):
            if template[a] == '$':
                if a + 2 < len(template) and re.search(r'\d', template[a + 2]):  # если двузначное число
                    n = int(template[a + 1:a + 3])
                    a += 3
                else:
                    n = int(template[a + 1])
                    a += 2

                if a < len(template):
                    next_symbol = template[a]
                else:
                    next_symbol = ''

                temp = ''
                while len(value) > b and value[b] != next_symbol:
                    temp += value[b]
                    b += 1
                result[n] = temp
            else:
                a += 1
                b += 1
        return result

    def parse_params(self, node: Node) -> str:
        if node.params == '':
            return ''
        with self.connection as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM {self.help_table_name} WHERE func_name = '{node.name}'")
            # print({node.name})
            params = list(cur.fetchone())
            for i in range(len(params)):
                if params[i].find('[') != -1:
                    params[i] = json.loads(params[i])
        params_dict = self.find_template_match(params[1], node.params)

        params_str = []
        for i, param_name in enumerate(params[2]):
            if params_dict[i + 1] == '%20':
                continue

            if str(params[3][i]).endswith('Enum'):
                if re.search(r'\d', params_dict[i + 1]):
                    params_str.append(f"{param_name}={params[3][i]}.{enums_numbers_to_str[int(params_dict[i + 1])]}")
                else:
                    params_str.append(f"{param_name}={params[3][i]}.{params_dict[i + 1].upper()}")
            elif params[3][i] == 'str':
                params_str.append(f"{param_name}='{params_dict[i + 1]}'")
            else:
                params_str.append(f"{param_name}={params_dict[i + 1]}")

        return ', '.join(params_str)

    def write_pam_node(self, node) -> str:
        def find_output_num(n: Node, input_num: int):
            for j in n.out_nodes:
                for k in range(len(n.out_nodes[j])):
                    if n.out_nodes[j][k].num_node == input_num:
                        return j
            return -1

        input_str = ''
        if node.in_nodes is not None:
            for i in range(1, len(node.in_nodes) + 1):
                if node.in_nodes[i].var_name.startswith('input') or node.in_nodes[i].var_name.startswith('output'):
                    input_str += f"{node.in_nodes[i].var_name} + "
                else:
                    output_num = find_output_num(node.in_nodes[i], node.num_node)
                    input_str += f"{node.in_nodes[i].var_name}[{output_num}] + "
            input_str = input_str[:-3]

        params_str = self.parse_params(node)

        if node.in_nodes is not None:
            if params_str == '':
                result = f"{node.var_name} = {node.name}({input_str})\n"
            else:
                result = f"{node.var_name} = {node.name}({input_str}, {params_str})\n"
        else:
            if params_str == '':
                result = f"{node.var_name} = {node.name}()\n"
            else:
                result = f"{node.var_name} = {node.name}({params_str})\n"
        return result

    def write_ous_node(self, node) -> str:
        def find_output_num(n: Node, input_num: int):
            for j in n.out_nodes:
                for k in range(len(n.out_nodes[j])):
                    if n.out_nodes[j][k].num_node == input_num:
                        return j
            return -1

        input_file = ''
        if node.in_nodes is not None:
            for i in range(1, len(node.in_nodes) + 1):
                if node.in_nodes[i].var_name.startswith('input') or node.in_nodes[i].var_name.startswith('output'):
                    input_file += f"{node.in_nodes[i].var_name}"
                else:
                    output_num = find_output_num(node.in_nodes[i], node.num_node)
                    input_file += f"{node.in_nodes[i].var_name}[{output_num}]"

        return f"save_file({input_file}, {node.var_name})\n"

    def write(self, nodes: List[Node]):
        ins_nodes = []
        out_nodes = []
        pam_nodes = []

        with open(self.file_name, 'w', encoding='utf-8') as file:
            file.write("from cvlib import *\n")
            file.write("from files_manager import File, save_file\n\n")

            # делим узлы по типу и генерируем имена для них
            for node in nodes:
                if node.type == 'INS':
                    node.var_name = self.generate_var_name(node_type='INS', starts_with='input_')
                    ins_nodes.append(node)
                if node.type == 'OUS':
                    node.var_name = self.generate_var_name(node_type='OUS', starts_with='output_')
                    out_nodes.append(node)
                if node.type == 'PAM':
                    node.var_name = self.generate_var_name(node_type='PAM')
                    pam_nodes.append(node)

            # записываем все input узлы в файл
            for node in ins_nodes:
                new_path = self.change_file_path(node.file)
                file.write(f"{node.var_name} = File(r'{new_path}')\n")
            file.write("\n")

            # записываем все output узлы в файл
            for node in out_nodes:
                new_path = self.change_file_path(node.file)
                file.write(f"{node.var_name} = r'{new_path}'\n")
            file.write("\n")

            # записываем сценарий, основанный на PAM узлах в файл
            for node in nodes:
                if node.type == 'OUS':
                    file.write(self.write_ous_node(node))
                if node.type == 'PAM':
                    file.write(self.write_pam_node(node))


class CVLibParallelWriter(CVLibWriter):
    def __init__(self, file_name: str):
        super().__init__(file_name)

    @staticmethod
    def fill_stages(sorted_nodes):
        # Проходимся по узлам, отсортированным в топологическом порядке
        for node in sorted_nodes:
            max_in_stage = 0
            # Проверяем входящие узлы текущего узла
            if node.in_nodes is not None:
                for i in range(1, len(node.in_nodes) + 1):
                    max_in_stage = max(max_in_stage, node.in_nodes[i].serial_num)
                node.serial_num = max_in_stage + 1
            else:
                node.serial_num = 1

    def parse_params(self, node: Node) -> str:
        if node.params == '':
            return ''
        with self.connection as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM {self.help_table_name} WHERE func_name = '{node.name}'")
            params = list(cur.fetchone())
            for i in range(len(params)):
                if params[i].find('[') != -1:
                    params[i] = json.loads(params[i])
        params_dict = self.find_template_match(params[1], node.params)

        params_str = []
        for i, param_name in enumerate(params[2]):
            if params_dict[i + 1] == '%20':
                continue

            if str(params[3][i]).endswith('Enum'):
                if re.search(r'\d', params_dict[i + 1]):
                    params_str.append(f"{params[3][i]}.{enums_numbers_to_str[int(params_dict[i + 1])]}")
                else:
                    params_str.append(f"{params[3][i]}.{params_dict[i + 1].upper()}")
            elif params[3][i] == 'str':
                params_str.append(f"'{params_dict[i + 1]}'")
            else:
                params_str.append(f"{params_dict[i + 1]}")

        return ', '.join(params_str)

    def write_parallel_pam_node(self, node) -> str:
        def find_output_num(n: Node, input_num: int):
            for j in n.out_nodes:
                for k in range(len(n.out_nodes[j])):
                    if n.out_nodes[j][k].num_node == input_num:
                        return j
            return -1

        input_str = ''
        if node.in_nodes is not None:
            for i in range(1, len(node.in_nodes) + 1):
                if node.in_nodes[i].var_name.startswith('input') or node.in_nodes[i].var_name.startswith('output'):
                    input_str += f"{node.in_nodes[i].var_name} + "
                else:
                    output_num = find_output_num(node.in_nodes[i], node.num_node)
                    input_str += f"{node.in_nodes[i].var_name}[{output_num}] + "
            input_str = input_str[:-3]

        params_str = self.parse_params(node)

        if node.in_nodes is not None:
            if params_str == '':
                result = '    ' + f"'{node.var_name}': {{'func': {node.name}, 'args': ({input_str},)}},\n"
            else:
                result = '    ' + f"'{node.var_name}': {{'func': {node.name}, 'args': ({input_str}, {params_str},)}},\n"
        else:
            if params_str == '':
                result = '    ' + f"'{node.var_name}': {{'func': {node.name}, 'args': ()}},\n"
            else:
                result = '    ' + f"'{node.var_name}': {{'func': {node.name}, 'args': ({params_str},)}},\n"
        return result

    def write(self, nodes: List[Node]):
        ins_nodes = []
        out_nodes = []
        pam_nodes = []

        # делим узлы по типу и генерируем имена для них
        for node in nodes:
            if node.type == 'INS':
                node.var_name = self.generate_var_name(node_type='INS', starts_with='input_')
                ins_nodes.append(node)
            if node.type == 'OUS':
                node.var_name = self.generate_var_name(node_type='OUS', starts_with='output_')
                out_nodes.append(node)
            if node.type == 'PAM':
                node.var_name = self.generate_var_name(node_type='PAM')
                pam_nodes.append(node)

        # находим стадии выполнения и заполняем вспомогательный словарь
        self.fill_stages(nodes)
        pam_nodes_by_stage = {}
        for pam_node in pam_nodes:
            stage_num = pam_node.serial_num
            if stage_num in pam_nodes_by_stage:
                pam_nodes_by_stage[stage_num].append(pam_node)
            else:
                pam_nodes_by_stage[stage_num] = [pam_node]

        with open(self.file_name, 'w', encoding='utf-8') as file:
            file.write("from cvlib import *\n")
            file.write("from cv_lib_parallel import CVLibParallel\n")
            file.write("from files_manager import File\n\n")

            file.write("def main(parallel_manager: CVLibParallel):\n")

            # записываем все input узлы в файл
            for node in ins_nodes:
                new_path = self.change_file_path(node.file)
                file.write('    ' + f"{node.var_name} = File(r'{new_path}')\n")
            file.write("\n")

            # записываем все output узлы в файл
            for node in out_nodes:
                new_path = self.change_file_path(node.file)
                file.write('    ' + f"{node.var_name} = r'{new_path}'\n")
            file.write("\n")

            # записываем сценарий, основанный на PAM узлах в файл
            for stage in pam_nodes_by_stage:
                if len(pam_nodes_by_stage[stage]) == 1:
                    file.write('    ' + self.write_pam_node(pam_nodes_by_stage[stage][0]))
                elif len(pam_nodes_by_stage[stage]) > 1:
                    file.write("\n")
                    file.write('    ' + "res = parallel_manager.run({\n")
                    for node in pam_nodes_by_stage[stage]:
                        file.write('    ' + self.write_parallel_pam_node(node))
                    file.write('    ' + "})\n")
                    for node in pam_nodes_by_stage[stage]:
                        file.write('    ' + f"{node.var_name} = res['{node.var_name}'].get()\n")
                    file.write("\n")

            file.write('if __name__ == "__main__":\n')
            # file.write('    ' + 'parallel_manager = CVLibParallel()\n')
            file.write('    ' + 'main(CVLibParallel())\n')


