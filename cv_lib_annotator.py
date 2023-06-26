from typing import List
from cv_lib_generator import CVLibGenerator
from ap_parser import Node
import sqlite3 as db


class CVLibAnnotator:
    def __init__(self, file_name: str, lang: str = 'RU'):
        self.file_name = file_name

        self.db_name = 'cvLib.db'
        if lang == 'RU':
            self.table_name = 'OperatorsRU'
        else:
            self.table_name = 'OperatorsEN'
        self.connection = db.connect('data/' + self.db_name)

    @staticmethod
    def get_in_nodes(node: Node):
        if node is None:
            return None
        else:
            if node.in_nodes is None:
                return None
            return [node.in_nodes[i + 1] for i in range(len(node.in_nodes))]

    def annotate(self, nodes: List[Node]):
        ins_nodes = []
        out_nodes = []
        pam_nodes = []

        # делим узлы по типу
        for node in nodes:
            if node.type == 'INS':
                ins_nodes.append(node)
            if node.type == 'OUS':
                out_nodes.append(node)
            if node.type == 'PAM':
                pam_nodes.append(node)

        with open(self.file_name, 'w', encoding='utf-8') as file:
            # записываем все input узлы в файл
            file.write("Входные данные:\n".upper())
            for i, node in enumerate(ins_nodes, start=1):
                file.write(f"{i}) {node.label} ({node.file.split('/')[-1]})\n")
            file.write("\n")

            file.write("Результат работы сценария:\n".upper())
            for i, node in enumerate(out_nodes, start=1):
                file.write(f"{i}) {node.label} ({node.file.split('/')[-1]})\n")
            file.write("\n")

            file.write("Аннотация к сценарию:\n".upper())

            # записываем сценарий, основанный на PAM узлах в файл
            for node in pam_nodes:
                in_nodes = CVLibAnnotator.get_in_nodes(node)
                msg = self.get_message_from_db(node.name)
                # если нет входных узлов
                if in_nodes is None:
                    file.write(f"{pam_nodes.index(node) + 1}. {CVLibGenerator.preprocess_message(msg)}\n")
                else:
                    ins = [in_node for in_node in in_nodes if in_node.type == 'INS']
                    pams = [in_node for in_node in in_nodes if in_node.type == 'PAM']

                    if len(ins) != 0 and len(pams) == 0:  # если оператор использует только входные файлы
                        if len(ins) == 1:
                            temp = f"{ins[0].label} ({ins[0].file.split('/')[-1]})"
                            from_info = f' берет данные из входного файла "{temp}" и '
                        else:
                            temp = f"{', '.join([i.label + ' (' + i.file.split('/')[-1] + ')' for i in ins])}"
                            from_info = f' берет данные из входных файлов "{temp}" и '
                    elif len(pams) != 0 and len(ins) == 0:  # если оператор использует только результаты других операторов
                        if len(pams) == 1:
                            from_info = f'Для результата из пункта {pam_nodes.index(pams[0]) + 1} '
                        else:
                            from_info = f'Для результатов из пунктов {", ".join([str(pam_nodes.index(o) + 1) for o in pams])} '
                    else:
                        if len(ins) == 1:
                            temp = f"{ins[0].label} ({ins[0].file.split('/')[-1]})"
                            from_info = f'берет данные из входного файла "{temp}" и '
                        else:
                            temp = f"{', '.join([i.label + ' (' + i.file.split('/')[-1] + ')' for i in ins])}"
                            from_info = f'берет данные из входных файлов "{temp}" и '
                        if len(pams) == 1:
                            from_info += f'для результата из пункта {pam_nodes.index(pams[0]) + 1} '
                        else:
                            from_info += f'для результатов из пунктов {", ".join([str(pam_nodes.index(o) + 1) for o in pams])} '

                    file.write(f"{pam_nodes.index(node) + 1}. {from_info}{CVLibGenerator.preprocess_message(msg)}\n")

    def get_message_from_db(self, node_name: str) -> str:
        with self.connection as con:
            cur = con.cursor()
            cur.execute(f"SELECT message FROM {self.table_name} WHERE name = '{node_name}'")
            msg = cur.fetchone()[0]
            return msg
