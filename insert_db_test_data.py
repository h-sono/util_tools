import os
import csv
import ast
from importlib import import_module
from django.core.exceptions import ObjectDoesNotExist


def insert_db_test_data(model, current_path, test_data_dir_path, file_name):
    """
    PythonユニットテストでDBにテストデータを登録する際に使用する。

    Args:
        model:テストデータを登録するモデル
        current_path:テストファイルが存在するパス
        test_data_dir_path:テストデータが配置されているパス
        file_name:テストデータを格納したCSVファイル

    CSVファイルへの登録の仕方:
        (1)外部キー
            カラム名は、「FK:カラム名:モデルクラス名」の形式とする。
            値は、"{'id':1}"のようにし、上記モデルクラス名に指定したテーブルを検索する際の検索条件を指定する。

        (2)リスト
            カラム名は、「LIST:カラム名」の形式とする。
            値は、"['hoge1', 'hoge2']"のようにする。

        (3)辞書
            カラム名は、「DICT:カラム名」の形式とする。
            値は、"{'hoge1':'1', 'hoge2':'test'}"のようにする。

    """
    with open(
        os.path.join(current_path + "/" + test_data_dir_path + "/" + file_name),
        "r",
        encoding="utf-8",
    ) as csv_file:
        csv_reader = csv.reader(csv_file)

        row_index = 0
        col_names = []
        data_list = []
        for row in csv_reader:
            if row_index == 0:
                col_names.extend(row)
            else:
                data_dict = {}
                col_index = 0
                for value in row:
                    if len(value) > 0:
                        if col_names[col_index].startswith("FK:"):
                            try:
                                search_val = ast.literal_eval(value)
                            except Exception:
                                raise ValueError(
                                    "CSVの外部キーの値(検索条件)には文字列型の辞書を指定してください。\n"
                                    "対象CSVファイル: '{0}'。\n"
                                    "外部キーに指定されている値: '{1}'。".format(file_name, value)
                                )

                            if type(search_val) == dict:
                                if len(col_names[col_index].split(":")) == 3:
                                    try:
                                        # モデルクラス取得。モデルクラスファイルが定義されているパスを指定。
                                        module = import_module("hoge.models")
                                        target_model = getattr(
                                            module, col_names[col_index].split(":")[2]
                                        )
                                    except AttributeError:
                                        raise ValueError(
                                            "CSVの外部キー(FK:カラム名:モデルクラス名)に指定したモデルが不正です。\n"
                                            "対象CSVファイル: '{0}'。\n"
                                            "CSVの外部キー名: '{1}'。".format(
                                                file_name, col_names[col_index]
                                            )
                                        )
                                    except Exception:
                                        raise Exception(
                                            "モデルクラス取得時に予期しないエラーが発生。\n"
                                            "対象CSVファイル: '{0}'。".format(file_name)
                                        )

                                    try:
                                        obj = target_model.objects.get(**search_val)
                                    except ObjectDoesNotExist:
                                        raise ValueError(
                                            "外部キーに対するモデルオブジェクトがテーブルから取得できません。\n"
                                            "検索対象テーブルにレコードが未登録、検索対象テーブル、検索条件に誤りがあります。\n"
                                            "対象CSVファイル: '{0}'。\n"
                                            "検索対象テーブル: '{1}'。\n"
                                            "検索条件: '{2}'。".format(
                                                file_name, target_model, search_val
                                            )
                                        )
                                    except Exception:
                                        raise Exception(
                                            "外部キーに対するモデルオブジェクト取得時(テーブル検索時)に予期しないエラーが発生。\n"
                                            "対象CSVファイル: '{0}'。".format(file_name)
                                        )

                                    data_dict[col_names[col_index].split(":")[1]] = obj
                                else:
                                    raise ValueError(
                                        "CSVの外部キーは「FK:カラム名:モデルクラス名」の形式としてください。\n"
                                        "対象CSVファイル: '{0}'。\n"
                                        "CSVの外部キー: '{1}'。".format(
                                            file_name, col_names[col_index]
                                        )
                                    )
                            # 値がリストの場合。
                            elif col_names[col_index].startswith("LIST:"):
                                try:
                                    list_val = ast.literal_eval(value)
                                except Exception:
                                    raise ValueError(
                                        "CSVにリストを登録する際には文字列型のリストとしてください。\n"
                                        "対象CSVファイル: '{0}'。\n"
                                        "カラムに指定されている値: '{1}'。".format(file_name, value)
                                    )
                                if type(list_val) == list:
                                    # リストに変換した値を格納。
                                    data_dict[
                                        col_names[col_index].split(":")[1]
                                    ] = list_val
                                else:
                                    raise ValueError(
                                        "リストを登録すべきカラムの値がリストではありません。\n"
                                        "リスト形式で登録してください。\n"
                                        "対象CSVファイル: '{0}'。\n"
                                        "カラムに指定されている値: '{1}'。".format(
                                            file_name, list_val
                                        )
                                    )
                            # 値が辞書の場合。
                            elif col_names[col_index].startswith("DICT:"):
                                try:
                                    dict_val = ast.literal_eval(value)
                                except Exception:
                                    raise ValueError(
                                        "CSVに辞書を登録する際には文字列型の辞書としてください。\n"
                                        "対象CSVファイル: '{0}'。\n"
                                        "カラムに指定されている値: '{1}'。".format(file_name, value)
                                    )
                                if type(dict_val) == dict:
                                    # 辞書に変換した値を格納。
                                    data_dict[
                                        col_names[col_index].split(":")[1]
                                    ] = dict_val
                                else:
                                    raise ValueError(
                                        "辞書を登録すべきカラムの値が辞書ではありません。\n"
                                        "辞書形式で登録してください。\n"
                                        "対象CSVファイル: '{0}'。\n"
                                        "カラムに指定されている値: '{1}'。".format(
                                            file_name, dict_val
                                        )
                                    )
                            else:
                                raise ValueError(
                                    "辞書を登録すべきカラムの値が辞書ではありません。辞書形式で登録してください。\n"
                                    "対象CSVファイル: '{0}'。\n"
                                    "カラムに指定されている値: '{1}'。".format(file_name, dict_val)
                                )
                        else:
                            # 外部キー、リスト、辞書以外はそのまま値を格納する。
                            data_dict[col_names[col_index]] = value
                    else:
                        # 指定した値が空の場合はNoneとする。
                        data_dict[col_names[col_index]] = None

                    col_index += 1

                data_list.append(data_dict)

            row_index += 1

        try:
            for data in data_list:
                model.objects.create(**data)
        except Exception:
            raise Exception(
                "登録対象テーブルまたは登録データが不正です。\n"
                "対象CSVファイル: '{0}'。\n"
                "model: '{1}'。\n"
                "data_list: '{2}'。".format(file_name, model, data_list)
            )
