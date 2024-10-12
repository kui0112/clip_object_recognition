import json
from typing import Dict

from excel_reader import read_object_configs


class Config:
    def __init__(self):
        # 物品配置
        self.object_configs = dict()

        # 字体文件
        self.font_file = r"D:\resources\Fonts\微软雅黑.ttf"
        # 识别设备，cpu or cuda
        self.device = "cuda"
        # CLIP 模型所在目录
        self.model_directory = r"D:\models"

        # 最高帧率
        self.fps = 25
        # 后端地址
        self.notify_url = "http://localhost:9999/update_display"
        self.enable_network_notify = True
        # 视频流地址
        self.video_stream = 1
        self.object_configs_file = "objectList.xlsx"

        # 所有texts
        self.texts = []
        # 索引
        self.index = dict()
        self.text2name = dict()

    def get_text_trigger_condition(self, text: str):
        name = self.text2name[text]
        return self.index[name]

    def parse(self, file: str):
        data: Dict = json.load(open(file, "r", encoding="utf-8"))

        obj_cfgs = read_object_configs(data["object_configs_file"])
        if not obj_cfgs:
            raise Exception("object_configs is null or empty.")

        data["object_configs"] = obj_cfgs

        self.__dict__.update(data)

        for obj in obj_cfgs:
            name = obj.get("name")
            text = obj.get("text")
            self.texts.append(text)
            self.index.update({name: obj})
            self.text2name.update({text: name})

        self.text2name.update({"nothing": ""})

        return self

    def to_dict(self):
        return self.__dict__


if __name__ == '__main__':
    cfg = Config().parse("config.json")
    print(cfg.to_dict())
