import data
from ap_parser import APparser
from cv_lib_generator import CVLibGenerator
from cv_lib_writer import CVLibWriter
from template_enums import *
import os

from files_manager import FilesManager


def main():
	file1 = 'data/prostak-db.ru_RU.UTF-8.sqlt3.in'
	file2 = 'data/convert.sqlt3.ru_RU.in'
	file3 = 'data/prostak-db.en_US.UTF-8.sqlt3.in'
	file4 = 'data/convert.sqlt3.en_US.in'
	creator = CVLibGenerator((file1, file2), (file3, file4))
	creator.run()

	# parser = APparser()


if __name__ == "__main__":
	# need_clean = input('Do you want to clean up the files left over from the previous run? (y/n)\n - ')
	# if need_clean == 'y' or need_clean == 'Y' or need_clean == 'yes' or need_clean == 'Yes' or need_clean == 'YES':
	FilesManager.clean_dir()

	main()

	parser = APparser()
	# nodes = parser.parse(r"C:\ProStack\share\prostack\examples\expr\extract_expression.ap")
	# nodes = parser.parse(r"E:\M_1C_4_dots_DI.ap")
	nodes = parser.parse(r"C:\ProStack\share\prostack\examples\k167\cells.ap")
	writer = CVLibWriter('result.py')
	writer.write(nodes)




