import os
from configparser import ConfigParser
import re


class Node(object):
    def __init__(self, num_node: int = 0):
        self.num_node: int = num_node
        self.in_nodes = None
        self.out_nodes = None
        self.serial_num: int = 0

        self.type: str = ''
        self.name: str = ''
        self.file: str = ''
        self.label: str = ''
        self.var_name: str = ''
        self.params: str = ''

        self.is_checked: bool = False

    def __eq__(self, other):
        if isinstance(other, Node) and other.num_node == self.num_node:
            return True
        return False

    def __hash__(self):
        return hash(self.num_node)


class APparser:
    nodes_grid = []

    @staticmethod
    def space_problem_fix(file_path: str):
        with open(file_path, 'r', encoding='utf-8') as file:
            old_file_str = file.read()
        regex = re.compile('%')

        if regex.search(old_file_str) is not None:
            new_file_str = re.sub('%', '%%', old_file_str)
            with open(file_path[:-3] + '.txt', 'w') as new_file:
                new_file.write(new_file_str)
            return file_path[:-3] + '.txt'
        else:
            return file_path

    def parse(self, file_path: str) -> []:
        new_file = self.space_problem_fix(file_path)

        config = ConfigParser()
        config.read(new_file)

        os.remove(new_file)

        self.create_grid(config)
        self.fill_nodes_info(config)
        self.fill_serial_numbers()
        return self.nodes_grid

    def is_in_grid(self, node_num: int) -> bool:
        return Node(node_num) in self.nodes_grid

    def get_node(self, node_num: int) -> Node:
        return self.nodes_grid[self.nodes_grid.index(Node(node_num))]

    def create_grid(self, config):
        # итерируемся по всем выходам узлов
        for out_node_str in config.options("Connections"):
            node_number = int(out_node_str.split(".")[0])
            node_output_num = int(out_node_str.split(".")[1])

            # добавляем узел в лист, если его там нет
            if not self.is_in_grid(node_number):
                self.nodes_grid.append(Node(node_number))

            # достаем узел из списка
            node = self.get_node(node_number)

            # если в данный узел входит более одного узла
            input_nodes = config.get("Connections", out_node_str).split(';')
            if len(input_nodes) > 1:
                input_nodes = input_nodes[:-1]

            # итерируемся по всем входящим узлам
            for input_node_str in input_nodes:
                input_node_number = int(input_node_str.split(".")[0])
                input_number = int(input_node_str.split(".")[1])

                # если такого узла еще нет в списке, добавляем
                if not self.is_in_grid(input_node_number):
                    temp_node = Node(input_node_number)
                    temp_node.in_nodes = {input_number: node}
                    self.nodes_grid.append(temp_node)
                else:
                    # иначе - достаем и исправляем
                    input_node = self.get_node(input_node_number)
                    if input_node.in_nodes is None:
                        input_node.in_nodes = {input_number: node}
                    else:
                        input_node.in_nodes.update({input_number: node})

                # достаем узел, чтобы добавить информацию о выходных узлах
                input_node = self.get_node(input_node_number)
                if node.out_nodes is None:
                    node.out_nodes = {node_output_num: [input_node]}
                else:
                    if node_output_num not in node.out_nodes:
                        node.out_nodes[node_output_num] = [input_node]
                    else:
                        node.out_nodes[node_output_num].append(input_node)

    def fill_nodes_info(self, config):
        # пока не заполним все узлы
        while not all(map(lambda n: n.is_checked, self.nodes_grid)):

            # идем по ap-файлу
            for section in config.sections():
                if 'Node:' in section:
                    node = self.get_node(int(section.split(':')[1]))
                    list_elements_of_node = config.options(section)
                    config_section = config[section]
                    if 'type' in list_elements_of_node:
                        node.type = config_section['type']
                    if 'name' in list_elements_of_node:
                        node.name = config_section['name']
                    if 'file' in list_elements_of_node:
                        node.file = config_section['file']
                    if 'id' in list_elements_of_node:
                        node.params = config_section['id']
                    if 'label' in list_elements_of_node:
                        node.label = config_section['label']
                    node.is_checked = True

    def fill_serial_numbers(self):
        in_degree = {Node: int}
        queue = []

        for node in self.nodes_grid:
            if node.in_nodes is None:
                in_degree[node] = 0
                queue.append(node)
            else:
                in_degree[node] = len(node.in_nodes)

        cnt = 0
        top_order = []

        while queue:
            u = queue.pop(0)
            top_order.append(u)

            if u.out_nodes is not None:
                for i in u.out_nodes:
                    for j in u.out_nodes[i]:
                        in_degree[j] -= 1
                        if in_degree[j] == 0:
                            queue.append(j)

            cnt += 1

        if cnt != len(self.nodes_grid):
            print("ERROR: there exists a cycle in the scenario")
        else:
            self.nodes_grid = top_order
