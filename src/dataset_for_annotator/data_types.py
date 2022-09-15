import datetime
from dataclasses import dataclass, asdict
from enum import Enum, unique
from typing import Any, Callable

from utils.file import PathLike, load_json, save_json

JSON_ELM = list | dict | int | str | None

# データセットで使うタイムスタンプは, 日本時間で統一
JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')

def date_handler(obj: Any) -> Any:
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

@unique
class MissingValue(str, Enum):
    """欠損値を扱うやつ"""

    Unacquired = "unacquired"
    """未取得: これから取得を試みる場合"""

    Failed = "failed"
    """取得失敗: 取得を試みたが, なんらかの理由でエラーになった場合"""

    NotExist = "not_exist"
    """存在しない: 取得を試みた結果, 存在しないことが分かった場合"""

    @classmethod
    def has_value(cls, value) -> bool:
        if isinstance(value, str):
            return value in cls._value2member_map_
        else:
            return False

def json_to_missing_value_or_any(
    json_elm: JSON_ELM, constructor: Callable[[JSON_ELM], Any] = lambda x: x
) -> Any | MissingValue:
    if MissingValue.has_value(json_elm):
        return MissingValue(json_elm)
    else:
        return constructor(json_elm)

@dataclass
class TwitterData:
    twitter_id: str
    name: str | None = None
    profile_text: str | None = None

    header_url: str | None = None
    icon_url: str | None = None

    follower_n: int | None = None
    follow_n: int | None = None

    recent_tweet_urls: list[str] | None = None
    pinned_tweet_url: str | None = None

    @classmethod
    def from_json(cls, json_dict: dict):
        return cls(**json_dict)

@dataclass
class YouTubeVideoData:
    video_id: str
    title: str | None = None
    description: str | None = None
    timestamp: datetime.datetime | None = None
    # playlist items で取得できないので, 必要性が出るまで見送り
    ## view_n: int | None
    ## good: int | None

    @classmethod
    def from_json(cls, json_dict: dict):
        if json_dict["timestamp"] is not None:
            json_dict["timestamp"] = datetime.datetime.fromisoformat(
                json_dict["timestamp"]
            )
        return cls(**json_dict)

@dataclass
class YouTubeData:
    channel_id: str
    name: str | None = None
    channel_description: str | None = None

    publish_time: datetime.datetime | None = None

    subscriber_count: int | None = None
    view_count: int | None = None
    video_count_n: int | None = None

    # brandSetting にあるじゃんと思ったけど, 取得出来る人とできない人がいるので却下
    ## country: str | None

    upload_videos: list[YouTubeVideoData] | None = None

    @classmethod
    def from_json(cls, json_dict: dict):
        if json_dict["publish_time"] is not None:
            json_dict["publish_time"] = datetime.datetime.fromisoformat(
                json_dict["publish_time"]
            )

        if json_dict["upload_videos"] is not None:
            json_dict["upload_videos"] = list(map(
                YouTubeVideoData.from_json, json_dict["upload_videos"]
            ))

        return cls(**json_dict)

@dataclass
class VTuberMergedData:
    vtuber_id: str
    create_at: datetime.datetime
    youtube: YouTubeData
    target_video: YouTubeVideoData | MissingValue = MissingValue.Unacquired
    twitter: TwitterData | MissingValue = MissingValue.Unacquired

    @classmethod
    def from_json(cls, json_dict: dict):
        json_dict["create_at"] = datetime.datetime.fromisoformat(
            json_dict["create_at"]
        )
        json_dict["twitter"] = json_to_missing_value_or_any(
            json_dict["twitter"],
            constructor = TwitterData.from_json
        )
        json_dict["youtube"] = YouTubeData.from_json(json_dict["youtube"])
        json_dict["target_video"] = json_to_missing_value_or_any(
            json_dict["target_video"],
            constructor = YouTubeVideoData.from_json
        )

        return cls(**json_dict)

def load_vtuber_merged_datum(json_path: PathLike) -> list[VTuberMergedData]:
    vtuber_merged_datum = load_json(json_path)
    return list(map(VTuberMergedData.from_json, vtuber_merged_datum))

def save_vtuber_merged_datum(datum: list[VTuberMergedData], json_path: PathLike) -> None:
    save_obj = [asdict(d) for d in datum]
    save_json(json_path, save_obj, date_handler)

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
    target_video_url: str

    @classmethod
    def from_json(cls, json_dict: dict):
        return cls(**json_dict)

@dataclass
class VTuberDatasetItem:
    vtuber_id: str
    create_at: datetime.datetime
    twitter: TwitterDatasetItem
    youtube: YouTubeDatasetItem

    @classmethod
    def from_json(cls, json_dict: dict):
        json_dict["create_at"] = datetime.datetime.fromisoformat(
            json_dict["create_at"]
        )
        json_dict["twitter"] = TwitterDatasetItem.from_json(json_dict["twitter"])
        json_dict["youtube"] = YouTubeDatasetItem.from_json(json_dict["youtube"])
        return cls(**json_dict)

    @classmethod
    def from_vtuber_merged_data(cls, data: VTuberMergedData):
        vtuber_id = data.vtuber_id
        create_at = data.create_at
        twitter = TwitterDatasetItem(
            data.twitter.twitter_id,
            data.twitter.name,
            data.twitter.profile_text,
            data.twitter.header_url,
            data.twitter.icon_url,
            data.twitter.recent_tweet_urls,
            data.twitter.pinned_tweet_url
        )
        youtube = YouTubeDatasetItem(
            data.youtube.channel_id,
            data.target_video.video_id
        )

        return cls(
            vtuber_id, create_at,
            twitter, youtube
        )


def load_vtuber_dataset_items(json_path: PathLike) -> list[VTuberDatasetItem]:
    vtuber_dataset_items = load_json(json_path)
    return list(map(VTuberDatasetItem.from_json, vtuber_dataset_items))

def save_vtuber_dataset_items(items: list[VTuberDatasetItem], json_path: PathLike) -> None:
    save_obj = [asdict(d) for d in items]
    save_json(json_path, save_obj, date_handler)

