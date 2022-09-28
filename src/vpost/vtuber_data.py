import json
import datetime
from dataclasses import dataclass, asdict

@dataclass
class VTuberData:
    name: str

    youtube_id: str | None = None
    youtube_description: str | None = None

    registrants_n: int | None = None
    play_times: int | None = None
    upload_videos: int | None = None

    group_name: str | None = None

    @classmethod
    def from_json(cls, json_dict: dict):
        return cls(**json_dict)

def load_vtuber_datum(json_path) -> list[VTuberData]:
    with open(json_path, "r", encoding="utf-8") as f:
        vtuber_data_dict = json.load(f)
    return [VTuberData.from_json(vdd) for vdd in vtuber_data_dict]

def save_vtuber_datum(datum: list[VTuberData], json_path) -> None:
    save_obj = [asdict(d) for d in datum]
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(save_obj, f, ensure_ascii=False, indent=4, separators=(',', ': '))



TIMESTAMP_FORMAT = "%Y/%m/%d %H:%M"

@dataclass
class VideoData:
    video_id: str
    title: str|None
    timestamp: datetime.datetime
    view_n: int|None
    good: int|None

    @classmethod
    def from_json(cls, json_dict:dict):
        json_dict["timestamp"] = datetime.datetime.strptime(
            json_dict["timestamp"], TIMESTAMP_FORMAT
        )
        return VideoData(**json_dict)



@dataclass
class VTuberDetails:
    youtube_id: str
    description: str|None
    twitter_id: str|None

    recent_videos: list[VideoData]

    @classmethod
    def from_json(cls, json_dict:dict):
        recent_videos = [VideoData.from_json(d) for d in json_dict["recent_videos"]]

        return cls(
            youtube_id = json_dict["youtube_id"],
            description =  json_dict.get("description"),
            twitter_id = json_dict.get("twitter_id"),
            recent_videos = recent_videos
        )

def load_detail_datum(json_path) -> list[VTuberDetails]:
    with open(json_path, "r", encoding="utf-8") as f:
        vtuber_details_dict = json.load(f)
    return [VTuberDetails.from_json(vdd) for vdd in vtuber_details_dict]

def date_handler(obj):
    return obj.strftime(TIMESTAMP_FORMAT) if hasattr(obj, 'isoformat') else obj

def save_detail_datum(datum: list[VTuberDetails], json_path) -> None:
    save_obj = [asdict(d) for d in datum]
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(save_obj, f, ensure_ascii=False, indent=4, separators=(',', ': '), default=date_handler)

