from typing import List

from ap_parser import Node

class CVLibWriter:
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.var_count = -1

    def generate_var_name(self, starts_with: str = '', ends_with: str = '') -> str:
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

        self.var_count += 1
        return starts_with + get_name(self.var_count) + ends_with

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

    def write(self, nodes: List[Node]):
        nodes = sorted(nodes, key=lambda node: node.serial_num)

        with open(self.file_name, 'w') as file:
            file.write("from cvlib import *\n")
            file.write("from files_manager import FilesManager\n\n")

            # выводим все INS в начале
            for node in nodes:
                if node.type == 'INS':
                    node.var_name = self.generate_var_name(starts_with='input_')
                    file.write(node.var_name + " = " + f"FilesManager('{node.file}')" + '\n')

            file.write("\n")

            # генерируем имена для всех узлов
            self.var_count = -1
            for node in nodes:
                if node.type == 'PAM':
                    node.var_name = self.generate_var_name()

            # генерируем имена для OUS узлов
            self.var_count = -1
            for node in nodes:
                if node.type == 'OUS':
                    node.var_name = self.generate_var_name(starts_with='output_')
                    file.write(node.var_name + " = " + f"FilesManager('{node.file}')" + '\n')

            file.write("\n")

            for node in nodes:
                print(f"{node.num_node} - {node.var_name} - #{node.serial_num}")
                if node.num_node == 32:
                    print(node.in_nodes)
                    print(node.out_nodes)

            # выводим все узлы
            for node in nodes:
                if node.type == 'PAM':
                    input_str = ''
                    if node.in_nodes is None:
                        input_str = ''
                    else:
                        for i in range(len(node.in_nodes)):
                            input_str += node.in_nodes[i + 1].var_name + ' + '
                        input_str = input_str[:-3] + ''
                    params_str = ''

                    result = node.var_name + ' = '
                    result += node.name + "(" + input_str + ")\n"
                    # result += node.name + "(" + input_str + "'" + node.params + "')\n"

                    file.write(result)


