import datetime
from dataclasses import dataclass, asdict

from utils.file import PathLike, load_json, save_json
from .common import MissingValue, json_to_missing_value_or_any, date_handler

@dataclass
class TwitterData:
    twitter_id: str
    """先頭の'@'は消すこと"""
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
        twitter_data = cls(**json_dict)
        if twitter_data.twitter_id:
            twitter_data.twitter_id.replace("@", "")
            return twitter_data
        else:
            return MissingValue.Unacquired

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

def load_youtube_video_datum(json_path: PathLike) -> list[YouTubeVideoData]:
    youtube_video_datum = load_json(json_path)
    return list(map(YouTubeVideoData.from_json, youtube_video_datum))

def save_youtube_video_datum(video_datum: list[YouTubeVideoData], json_path: PathLike) -> None:
    save_obj = [asdict(v) for v in video_datum]
    save_json(json_path, save_obj, date_handler)

@dataclass
class YouTubeData:
    channel_id: str
    name: str | None = None
    channel_description: str | None = None

    publish_time: datetime.datetime | None = None

    subscriber_count: int | None = None
    view_count: int | None = None
    video_count_n: int | None = None
    got_video_n: int | None = None

    # brandSetting にあるじゃんと思ったけど, 取得出来る人とできない人がいるので却下
    ## country: str | None

    @classmethod
    def from_json(cls, json_dict: dict):
        if json_dict["publish_time"] is not None:
            json_dict["publish_time"] = datetime.datetime.fromisoformat(
                json_dict["publish_time"]
            )

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

