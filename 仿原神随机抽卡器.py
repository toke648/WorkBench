import pandas as pd
import openpyxl
from openpyxl import ExcelWriter, Cell

# file_path = './gate_data.xlsx'
# df = pd.read_excel(file_path)

# print(df.head())


# # 读取Excel文件
# file_path = 'gate_data.xlsx'  # 替换为你的文件路径
# df = pd.read_excel(file_path, engine='xlrd')  # 明确指定引擎

# # 显示数据
# print(df)

writer = ExcelWriter('gate_data.xlsx', overtime='auto')
sheet = writer.sheets['Sheet1']

print(sheet)