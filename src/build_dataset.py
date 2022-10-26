"""vpost と YouTube から取得したデータをまとめて, さらに足りないデータも集めて, データセットを作る.
"""
import os

from dotenv import load_dotenv

from dataset_for_annotator.dataset_builder import DatasetBuilder

VPOST_DATA_PATH = "vpost_data/vtuber_data.json"
VPOST_DETAIL_PATH = "vpost_data/detail_data.json"
YOUTUBE_DATA_PATH = "yt_data/channels.json"

load_dotenv()

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
TWITTER_API_KEY = ""

builder = DatasetBuilder("dataset", YOUTUBE_API_KEY, TWITTER_API_KEY, 2000, True)
builder.load_merged_datum()
# builder.load_upload_videos()
# builder.load_vpostdata(VPOST_DATA_PATH, VPOST_DETAIL_PATH)
# builder.load_ytdata(YOUTUBE_DATA_PATH)

builder.build()

