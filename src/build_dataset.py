
from dataset_for_annotator.dataset_builder import DatasetBuilder

VPOST_DATA_PATH = "vpost_data/vtuber_data.json"
VPOST_DETAIL_PATH = "vpost_data/detail_data.json"
YOUTUBE_DATA_PATH = "yt_data/channels.json"

builder = DatasetBuilder("dataset")
builder.load_vpostdata(VPOST_DATA_PATH, VPOST_DETAIL_PATH)
builder.load_ytdata(YOUTUBE_DATA_PATH)
