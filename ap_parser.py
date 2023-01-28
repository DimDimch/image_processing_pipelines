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
        self.var_name: str = ''
        self.params: str = ''

        self.is_checked: bool = False

    def __eq__(self, other):
        if isinstance(other, Node) and other.num_node == self.num_node:
            return True
        return False


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

        # заполняем выходы узла
        for node in self.nodes_grid:
            if node.in_nodes is None:
                pass
            else:
                for i in range(len(node.in_nodes)):
                    input_node = node.in_nodes[i + 1]
                    if input_node.out_nodes is None:
                        input_node.out_nodes = {1: node}
                    else:
                        input_node.out_nodes.update({len(input_node.out_nodes) + 1: node})

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
                    node.is_checked = True

    def fill_serial_numbers(self):
        visited = {}
        result = {int: []}

        def dfs(start: int, visited):
            if start not in list(visited.keys()):
                visited[start] = 0

            # if self.get_node(start).num_node == 33:
            #     print(start)

            if self.get_node(start).in_nodes is None:
                len_in_nodes = 0
            else:
                len_in_nodes = len(self.get_node(start).in_nodes)

            if visited[start] <= len_in_nodes:
                visited[start] += 1
                out_nodes = self.get_node(start).out_nodes
                in_nodes = self.get_node(start).in_nodes
                max_serial_num = 0

                if in_nodes is not None:
                    for i in range(len(in_nodes)):
                        if in_nodes[i + 1].serial_num + 1 > max_serial_num:
                            max_serial_num = in_nodes[i + 1].serial_num + 1
                    self.get_node(start).serial_num = max_serial_num

                if max_serial_num in result:
                    result[max_serial_num].append(start)
                else:
                    result[max_serial_num] = [start]

                if out_nodes is not None:
                    for i in range(len(out_nodes)):
                        neighbour = out_nodes[i + 1].num_node
                        dfs(neighbour, visited)

        for node in self.nodes_grid:
            if node.in_nodes is None:
                dfs(node.num_node, visited)
        for pair in result:
            print(pair, result[pair])
