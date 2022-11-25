"""
youtube-dlp だかなんだかで学習に使う用のデータを落としてくる
前処理はしない

自然言語処理的なものは後回しでいいかな
file name スネークケースにリネームする
"""

import os
import time
import glob
import logging
from yt_dlp import YoutubeDL, DownloadError

from dataset_for_annotator.data_types import dataset
from dataset_for_annotator.data_types.dataset import VTuberDatasetItem, load_vtuber_dataset_items
from utils.file import PathLike
from utils.logger import get_logger

def video_id_to_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"

def is_exist_video(dir: str, video_id: str) -> bool:
    hitted = glob.glob(f"{dir}/*{video_id}*.mp4")
    return len(hitted) > 0

class VideoDownloader:
    def __init__(self,
        dataset_json_path: PathLike, save_dir: PathLike,
        logger: logging.Logger = get_logger(__name__, logging.DEBUG)
    ):
        self.dataset_json_path = dataset_json_path
        self.save_dir = save_dir
        self.logger = logger

        self.ydl = YoutubeDL({
            "format": "bv*[height<=480][ext=mp4]+ba[ext=m4a]/b[height<=480][ext=mp4]",
            "paths": {"home": self.save_dir},
        })

        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def download_dataset_videos(self):
        self.logger.info("start to download dataset videos")
        self.__load_dataset()

        for item in self.dataset_items:
            self.download_yt_video(item.youtube.target_video.video_id)

        self.logger.info("DONE!")

    def __load_dataset(self):
        self.dataset_items = load_vtuber_dataset_items(self.dataset_json_path)
        self.logger.info(f"loaded {len(self.dataset_items)} dataset items")

    def download_yt_video(self, video_id: str):
        if is_exist_video(self.save_dir, video_id):
            self.logger.info(f"{video_id} already exists")
            return None
        self.logger.info(f"downloading {video_id}")
        url = video_id_to_url(video_id)

        try:
            self.ydl.download(url)
        except DownloadError as e:
            self.logger.warning(f"ERROR at {video_id}")
            self.logger.warning(f"{e}")
            return None
        self.logger.info(f"downloaded {video_id}")

        time.sleep(3)