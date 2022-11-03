import pandas as pd

# csvファイルの読み込み
data = pd.read_csv('test_file.csv')

# excel形式で出力(カレントディレクトリへ出力)
data.to_excel('convert_to_excel.xlsx', encoding='utf-8')
