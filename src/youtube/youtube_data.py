import json
import datetime
from dataclasses import dataclass, asdict

def str_to_datetime(timestamp: str) -> datetime.datetime:
    timestamp = timestamp.replace("Z", "+00:00")
    return datetime.datetime.fromisoformat(timestamp)


@dataclass
class SearchResultItem:
    kind: str
    video_id: str

    publish_time: datetime.datetime

    title: str
    description: str

    channel_id: str
    channel_title: str

    @classmethod
    def from_json(cls, json_dict: dict):
        json_dict["publish_time"] = str_to_datetime(json_dict["publish_time"])
        return cls(**json_dict)

@dataclass
class SearchResult:
    timestamp: datetime.datetime
    query: str
    order: str
    items: list[SearchResultItem]

    @classmethod
    def from_json(cls, json_dict: dict):
        items = [SearchResultItem.from_json(d) for d in json_dict["items"]]

        return cls(
            timestamp = str_to_datetime(json_dict["timestamp"]),
            query = json_dict["query"],
            order = json_dict["order"],
            items = items
        )

def load_search_datum(json_path) -> list[SearchResult]:
    with open(json_path, "r", encoding="utf-8") as f:
        search_results_dict = json.load(f)
        return [SearchResult.from_json(vdd) for vdd in search_results_dict]

def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

def save_search_datum(datum: list[SearchResult], json_path) -> None:
    save_obj = [asdict(d) for d in datum]
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(save_obj, f, ensure_ascii=False, indent=4, separators=(',', ': '), default=date_handler)

@dataclass
class YouTubeChannelData:
    channel_id: str

    title: str
    description: str

    publish_time: datetime.datetime

    upload_list_id: str
    view_count: int
    subscriver_count: int | None # 非公開なら None
    video_count: int

    @classmethod
    def from_json(cls, json_dict: dict):
        json_dict["publish_time"] = str_to_datetime(json_dict["publish_time"])
        return cls(**json_dict)


def load_channel_datum(json_path) -> list[YouTubeChannelData]:
    with open(json_path, "r", encoding="utf-8") as f:
        channel_data_dict = json.load(f)
        return [YouTubeChannelData.from_json(vdd) for vdd in channel_data_dict]

def save_channel_datum(datum: list[YouTubeChannelData], json_path) -> None:
    save_obj = [asdict(d) for d in datum]
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(save_obj, f, ensure_ascii=False, indent=4, separators=(',', ': '), default=date_handler)
