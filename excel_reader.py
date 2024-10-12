from typing import Dict

import pandas
import json


def read_object_configs(filename: str):
    dataframe = pandas.read_excel(filename, sheet_name='Sheet1')

    dataframe.dropna(axis=0, how="any", subset=["name", "text"], inplace=True)

    json_string = dataframe.to_json(orient='records')
    data = json.loads(json_string)

    # post process
    for item in data:
        item: Dict

        del item["物品"]
        del item["测试状态"]
        del item["note"]
        del item["group"]
        del item["数量"]

    return data


if __name__ == '__main__':
    objects = read_object_configs("objectList.xlsx")
    print(json.dumps(objects, ensure_ascii=False))
