import datetime
from dataclasses import dataclass, asdict

from utils.file import PathLike, load_json, save_json
from .common import date_handler
from .merged import YouTubeVideoData, VTuberMergedData

@dataclass
class TwitterDatasetItem:
    twitter_id: str
    name: str
    profile_text: str

    header_url: str
    icon_url: str

    recent_tweet_urls: list[str]
    pinned_tweet_url: str | None = None

    @classmethod
    def from_json(cls, json_dict: dict):
        return cls(**json_dict)

@dataclass
class YouTubeDatasetItem:
    channel_id: str
    name: str
    target_video: YouTubeVideoData

    @classmethod
    def from_json(cls, json_dict: dict):
        json_dict["target_video"] = YouTubeVideoData.from_json(json_dict["target_video"])
        return cls(**json_dict)

@dataclass
class VTuberDatasetItem:
    vtuber_id: str
    create_at: datetime.datetime
    # twitter: TwitterDatasetItem # いったんTwitterの使用はやめる
    youtube: YouTubeDatasetItem

    @classmethod
    def from_json(cls, json_dict: dict):
        json_dict["create_at"] = datetime.datetime.fromisoformat(
            json_dict["create_at"]
        )
        json_dict["youtube"] = YouTubeDatasetItem.from_json(json_dict["youtube"])
        return cls(**json_dict)

    @classmethod
    def from_vtuber_merged_data(cls, data: VTuberMergedData):
        vtuber_id = data.vtuber_id
        create_at = data.create_at
        youtube = YouTubeDatasetItem(
            data.youtube.channel_id,
            data.youtube.name,
            data.target_video
        )

        return cls(
            vtuber_id, create_at, youtube
        )


def load_vtuber_dataset_items(json_path: PathLike) -> list[VTuberDatasetItem]:
    vtuber_dataset_items = load_json(json_path)
    return list(map(VTuberDatasetItem.from_json, vtuber_dataset_items))

def save_vtuber_dataset_items(items: list[VTuberDatasetItem], json_path: PathLike, shape_output: bool = True) -> None:
    save_obj = [asdict(d) for d in items]
    save_json(json_path, save_obj, date_handler, shape_output)

