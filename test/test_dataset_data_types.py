import pytest

import os
import datetime

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "src"))


from src.dataset_for_annotator.data_types import *

TEMP_DIR = Path("temp")
os.makedirs(TEMP_DIR, exist_ok=True)

@pytest.fixture
def vtuber_merged_datum() -> list[VTuberMergedData]:
    return [
        VTuberMergedData(
            "TestCase1-Init",
            datetime.datetime.fromisoformat("2022-01-01T00:00:00+09:00"),
            YouTubeData("TestCase1-Init"),
            MissingValue.Unacquired,
            MissingValue.Failed
        ),
        VTuberMergedData(
            "TestCase2-Minimum",
            datetime.datetime.fromisoformat("2022-01-01T12:00:05+09:00"),
            YouTubeData(
                "TestCase2-Minimum", "Test Ch. 最小 限", "必要最小限のパターンの VTuber です。",
                datetime.datetime.fromisoformat("2019-01-20T21:17:05+09:00"), None, 5000, 2,
                [
                    YouTubeVideoData("video1", "テスト投稿と野宿", "テストです。", datetime.datetime.fromisoformat("2019-01-30T00:00:00+09:00")),
                    YouTubeVideoData("video2", "テストその2 逃亡", "チャンネル登録おねがいします", datetime.datetime.fromisoformat("2019-01-31T00:00:00+09:00"))
                ]
            ),
            MissingValue.NotExist,
            TwitterData("twitter-minimum")
        ),
        VTuberMergedData(
            "TestCase3-Full",
            datetime.datetime.fromisoformat("2022-10-01T15:12:01+09:00"),
            YouTubeData(
                "TestCase3-Full", "Test Ch. 全要素 アリ", "全ての情報が取得できた VTuber です。",
                datetime.datetime.fromisoformat("2019-04-01T09:05:10+09:00"), 1500, 125141, 5,
                [
                    YouTubeVideoData(
                        "video1", "【VTuber自己紹介】はじめまして。全要素 アリです。",
                        "ハロハロ！〇〇VTuberの全要素 アリです。これからよろしくおねがいします。",
                        datetime.datetime.fromisoformat("2019-04-20T08:30:00+09:00")
                    ),
                    YouTubeVideoData(
                        "video2", "【初配信】これからやりたいこと！",
                        "ファンネーム決めたり、今後の活動予定話したりします！",
                        datetime.datetime.fromisoformat("2019-04-28T21:00:30+09:00")
                    ),
                    YouTubeVideoData(
                        "video3", "【ゲーム実況】我々はアマゾンの奥地へと向かった",
                        "こちらのゲームを実況します → wwwhogehogecom",
                        datetime.datetime.fromisoformat("2019-05-10T21:01:00+09:00")
                    ),
                    YouTubeVideoData(
                        "video4", "hogefuga 歌ってみた。 / 全要素 アリ cover",
                        "本家様 → aaaaa \n mix: xxxx",
                        datetime.datetime.fromisoformat("2019-05-20T20:00:00+09:00")
                    ),
                    YouTubeVideoData(
                        "video5", "【雑談配信】ぐでぇ～",
                        "最近憂鬱",
                        datetime.datetime.fromisoformat("2019-06-08T21:10:28+09:00")
                    )
                ]
            ),
            YouTubeVideoData(
                "video1", "【VTuber自己紹介】はじめまして。全要素 アリです。",
                "ハロハロ！〇〇VTuberの全要素 アリです。これからよろしくおねがいします。",
                datetime.datetime.fromisoformat("2019-04-20T08:30:00+09:00")
            ),
            TwitterData(
                "testcasefull", "全要素アリ@VTuber", "VTuberやってます！",
                "header-url", "icon-url", 1500, 321, [
                    "tweet1", "tweet2", "tweet3", "tweet4", "tweet5", "tweet6"
                ], None
            )
        )
    ]

@pytest.fixture
def vtuber_dataset_items() -> list[VTuberDatasetItem]:
    # 末尾のアイテムは, vtuber_merged_datum の末尾のアイテムを変換したものになっている
    return [
        VTuberDatasetItem(
            "TestCase1-hoge", datetime.datetime.fromisoformat("2022-10-10T15:12:01+09:00"),
            TwitterDatasetItem(
                "testcasehoge", "ほげほげふが@新人VTuber", "フォローしてください",
                "header-url-hoge", "icon-url-hoge", ["tweet-hoge", "tweet-fuga"], "tweet-pinned"
            ),
            YouTubeDatasetItem(
                "TestCase1-hoge", "self-intro-video"
            )
        ),
        VTuberDatasetItem(
            "TestCase3-Full", datetime.datetime.fromisoformat("2022-10-01T15:12:01+09:00"),
            TwitterDatasetItem(
                "testcasefull", "全要素アリ@VTuber", "VTuberやってます！",
                "header-url", "icon-url", [
                    "tweet1", "tweet2", "tweet3", "tweet4", "tweet5", "tweet6"
                ], None
            ),
            YouTubeDatasetItem(
                "TestCase3-Full", "video1"
            )
        )
    ]

def test_vtuber_merged_data(vtuber_merged_datum):
    JSON_NAME = "test_vtuber_merged_datum.json"
    save_vtuber_merged_datum(vtuber_merged_datum, TEMP_DIR.joinpath(JSON_NAME))
    loaded_datum = load_vtuber_merged_datum(TEMP_DIR.joinpath(JSON_NAME))
    assert loaded_datum == vtuber_merged_datum

def test_vtuber_dataset_item(vtuber_dataset_items):
    JSON_NAME = "test_vtuber_dataset_items.json"
    save_vtuber_dataset_items(vtuber_dataset_items, TEMP_DIR.joinpath(JSON_NAME))
    loaded_datum = load_vtuber_dataset_items(TEMP_DIR.joinpath(JSON_NAME))
    assert loaded_datum == vtuber_dataset_items

def test_merged_data_to_dataset_item(vtuber_dataset_items, vtuber_merged_datum):
    converted = VTuberDatasetItem.from_vtuber_merged_data(vtuber_merged_datum[-1])
    assert converted == vtuber_dataset_items[-1]
