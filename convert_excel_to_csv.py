import csv

import openpyxl
import pandas as pd

# ファイル名
file_name = 'test_file'
# 拡張子
extention = '.xlsx'
# ファイル名 + 拡張子
excel_name = file_name + extention

# シート名をリストで取得
input_book = pd.ExcelFile(excel_name)
input_sheet_name = input_book.sheet_names

# エクセルファイル読み込み
work_book = openpyxl.load_workbook(excel_name)
# 特定シートを指定(シートの番号をインデックス番号で指定)
work_sheet = work_book[input_sheet_name[0]]

# シートの行データを取得
all_rows_list = []
for row in work_sheet.iter_cols():
    row_list = []
    for cell in row:
        # IntegerFieldのカラムにはエクセルファイル側で事前に数値を入れる必要あり。
        # それ以外の空白セルは文字列型のカラムと判断し、Noneが来たら空文字とする。
        if cell.value is None:
            cell.value = ''
            row_list.append(str(cell.value))
        else:
            row_list.append(str(cell.value))
    all_rows_list.append(row_list)

# csvファイルへの書き込み
with open('result.csv', 'w') as f:
    writer = csv.writer(f)
    for item in all_rows_list:
        writer.writerow(item)
