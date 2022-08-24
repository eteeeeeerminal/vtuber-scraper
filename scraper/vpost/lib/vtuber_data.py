import json
from dataclasses import dataclass, asdict

@dataclass
class VTuberData:
    name: str

    twitter_id: str | None = None

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


