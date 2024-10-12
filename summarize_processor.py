import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Tuple, Optional

import requests
from PIL import Image

from config import Config
from processor import Processor
from main_context import FrameRecord


class SummarizeProcessor(Processor):
    def __init__(self, cfg: Config, network_enabled=False):
        self.cfg = cfg
        self.texts = cfg.texts
        # 每个text的缓冲区大小
        self.frame_records_buffer_size = 300
        self.frame_records: Dict[str, List[FrameRecord]] = {self.texts[i]: [] for i in range(len(self.texts))}
        # 上次汇总的时间戳（秒）
        self.previous_summarize_time = 0
        self.network_enabled = network_enabled
        self.executor: Optional[ThreadPoolExecutor] = None

    def initialize(self):
        self.executor = ThreadPoolExecutor(max_workers=4)

    def process(self, image: Image.Image, res: List[Tuple]):
        # 保存这一帧的识别结果
        self.save_record(res)

        now = time.time()
        if now - self.previous_summarize_time > 3:
            selected_res = "nothing"
            selected_prob = 0
            for text, prob in res:
                condition = self.cfg.get_text_trigger_condition(text)
                threshold = condition.get("trigger_prob_threshold")
                summary_pass, average_prob = self.summarize(text)
                if prob >= threshold and summary_pass:
                    selected_res = text
                    selected_prob = average_prob

            print(f"recognition result: {selected_res}, probability: {selected_prob}.")
            if self.network_enabled:
                try:
                    name = self.cfg.text2name.get(selected_res)
                    self.executor.submit(self.notify_through_network, name, selected_prob)
                except Exception as ex:
                    pass

            self.previous_summarize_time = now

    def destroy(self):
        self.executor.shutdown(wait=False)

    def notify_through_network(self, name: str, prob: float):
        try:
            requests.get(self.cfg.notify_url, {"object_name": name, "prob": prob}, timeout=1)
        except Exception as ex:
            print(ex)

    def summarize(self, text: str):
        condition = self.cfg.get_text_trigger_condition(text)
        summarize_frames = condition.get("summarize_frames")
        frame_proportion = condition.get("frame_proportion")

        records = self.frame_records[text]
        if len(records) < summarize_frames:
            return False, 0

        selected_records = list(filter(lambda x: x.reach_trigger_condition, records[len(records) - summarize_frames:]))
        if not len(selected_records):
            return False, 0

        proportion = len(selected_records) / summarize_frames
        prob = sum(list(map(lambda x: x.prob, selected_records))) / len(selected_records)

        return proportion >= frame_proportion, prob

    def save_record(self, values: List[Tuple[str, float]]):
        for i, (text, prob) in enumerate(values):
            i: int
            records = self.frame_records[text]
            condition = self.cfg.get_text_trigger_condition(text)
            summarize_prob = condition.get("summarize_prob")
            records.append(FrameRecord(prob, prob >= summarize_prob))
            while len(records) > self.frame_records_buffer_size / 2:
                records.pop(0)
