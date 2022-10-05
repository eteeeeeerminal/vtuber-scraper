import pytest

import os
import datetime

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "src"))


from dataset_for_annotator.data_types.common import *
from dataset_for_annotator.data_types.merged import *
from dataset_for_annotator.data_types.dataset import *

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
                datetime.datetime.fromisoformat("2019-01-20T21:17:05+09:00"), None, 5000, 2, 2
            ),
            MissingValue.NotExist,
            TwitterData("twitter-minimum")
        ),
        VTuberMergedData(
            "TestCase3-Full",
            datetime.datetime.fromisoformat("2022-10-01T15:12:01+09:00"),
            YouTubeData(
                "TestCase3-Full", "Test Ch. 全要素 アリ", "全ての情報が取得できた VTuber です。",
                datetime.datetime.fromisoformat("2019-04-01T09:05:10+09:00"), 1500, 125141, 5, 5
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
            YouTubeDatasetItem(
                "TestCase1-hoge", "テストくん",
                YouTubeVideoData(
                    "videohoge", "hogehogeohge",
                    "ほげほげです",
                    datetime.datetime.fromisoformat("2020-08-10T07:30:00+09:00")
                )
            )
        ),
        VTuberDatasetItem(
            "TestCase3-Full", datetime.datetime.fromisoformat("2022-10-01T15:12:01+09:00"),
            YouTubeDatasetItem(
                "TestCase3-Full", "Test Ch. 全要素 アリ",
                YouTubeVideoData(
                    "video1", "【VTuber自己紹介】はじめまして。全要素 アリです。",
                    "ハロハロ！〇〇VTuberの全要素 アリです。これからよろしくおねがいします。",
                    datetime.datetime.fromisoformat("2019-04-20T08:30:00+09:00")
                ),
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
