from distutils.command.upload import upload
import logging
import pathlib
import os
import datetime

from utils.file import PathLike
from utils.logger import get_logger
from youtube.youtube_data import YouTubeChannelData, load_channel_datum

from .data_types import JST, MissingValue, TwitterData, VTuberMergedData, YouTubeData, YouTubeVideoData, save_vtuber_merged_datum, load_vtuber_merged_datum
from .data_collector import TwitterCollector, YouTubeCollector
from .data_filter import got_upload_lists, tried_to_get_self_intro_video
from vpost.vtuber_data import VTuberData, VTuberDetails, VideoData, load_detail_datum, load_vtuber_datum

# ちょっとどこに置くか考える必要あるかも
def videodata_to_youtube_videodata(video_data: VideoData) -> YouTubeVideoData:
    video_data.timestamp = video_data.timestamp.replace(tzinfo=JST)
    return YouTubeVideoData(
        video_data.video_id, video_data.title,
        None, video_data.timestamp
    )

class DatasetBuilder:
    MERGED_JSON_NAME = "merged.json"
    DATASET_JSON_NAME = "dataset.json"

    def __init__(self,
        save_dir: PathLike, youtube_api_key: str,
        logger: logging.Logger = get_logger(__name__, logging.INFO)
    ) -> None:
        self.logger = logger

        save_dir = pathlib.Path(save_dir)
        os.makedirs(save_dir, exist_ok=True)
        self.merged_json_path = save_dir.joinpath(self.MERGED_JSON_NAME)
        self.dataset_json_path = save_dir.joinpath(self.DATASET_JSON_NAME)

        self.vtuber_merged_datum: dict[str, VTuberMergedData] = {}
        """key: vtuber_id, value: VTuberMergedData"""

        self.youtube_collector = YouTubeCollector(youtube_api_key, self.logger)

    def load_merged_datum(self) -> None:
        if not os.path.exists(self.merged_json_path):
            self.logger.info(f"{self.merged_json_path} is not found")
            return
        self.logger.info(f"START TO LOAD MERGED DATA from {self.merged_json_path}")
        vtuber_merged_datum = load_vtuber_merged_datum(self.merged_json_path)
        for data in vtuber_merged_datum:
            self.vtuber_merged_datum[data.vtuber_id] = data
        self.logger.info(f"DONE! merged data has loaded")

    def build(self) -> None:
        self.__filter_youtube_basic_info()
        self.__complement_youtube_basic_info()
        self.__filter_youtube_basic_info()
        self.__collect_youtube_data()
        self.__filter_youtube_content_info()

        self.__collect_twitter_data()

        self.__filter_all_data()
        self.__output_dataset()

    def load_vpostdata(self,
        vpost_data_json_path: PathLike, vpost_detail_json_path: PathLike,
        does_update: bool = False
    ) -> None:

        self.logger.info(f"START TO LOAD VPOST DATA: does_update is {does_update}")

        self.logger.info(f"load VTuberData from {vpost_data_json_path}")
        vpost_vtuber_datum: list[VTuberData] = load_vtuber_datum(vpost_data_json_path)

        for data in vpost_vtuber_datum:
            if not does_update and data.youtube_id in self.vtuber_merged_datum:
                # データの更新なし
                self.logger.debug(f"{data.youtube_id} is already exist. skip.")
                continue

            self.logger.debug(f"create or update {data.youtube_id}")
            self.vtuber_merged_datum[data.youtube_id] = VTuberMergedData(
                data.youtube_id,
                datetime.datetime.now(JST),
                YouTubeData(
                    data.youtube_id, data.name,
                    data.youtube_description, None,
                    data.registrants_n, data.play_times, data.upload_videos
                ),
                MissingValue.Unacquired,
                MissingValue.Unacquired if data.twitter_id else TwitterData(data.twitter_id)
            )

        self.logger.info(f"load VTuberDetails from {vpost_detail_json_path}")
        vpost_vtuber_detail: list[VTuberDetails] = load_detail_datum(vpost_detail_json_path)

        for detail in vpost_vtuber_detail:
            if not does_update and data.youtube_id in self.vtuber_merged_datum:
                # データの更新なし
                continue

            if detail.youtube_id not in self.vtuber_merged_datum:
                self.logger.info(f"VTuberData correspond to {detail.youtube_id} is not exist. skip.")
                continue

            merged_data = self.vtuber_merged_datum[detail.youtube_id]
            merged_data.youtube.channel_description = detail.description
            if detail.recent_videos:
                merged_data.youtube.upload_videos = list(
                    map(videodata_to_youtube_videodata, detail.recent_videos)
                )

            merged_data.twitter = MissingValue.Unacquired if detail.twitter_id else TwitterData(detail.twitter_id)

        self.logger.info(f"DONE! vpost data has loaded")
        self.__save_merged_datum()


    def load_ytdata(self, youtube_json_path: PathLike, does_update: bool = False) -> None:
        self.logger.info(f"START TO LOAD YOUTUBE DATA: does_update is {does_update}")

        self.logger.info(f"load YouTubeChannelData from {youtube_json_path}")
        channel_datum: list[YouTubeChannelData] = load_channel_datum(youtube_json_path)

        for data in channel_datum:
            if not does_update and data.channel_id in self.vtuber_merged_datum:
                self.logger.debug(f"{data.channel_id} is already exist. skip.")
                continue

            self.vtuber_merged_datum[data.channel_id] = VTuberMergedData(
                data.channel_id, datetime.datetime.now(JST),
                YouTubeData(
                    data.channel_id, data.title, data.description,
                    data.publish_time.replace(tzinfo=JST),
                    data.subscriber_count, data.view_count, data.video_count
                ),
                MissingValue.Unacquired,
                MissingValue.Unacquired
            )

        self.logger.info(f"DONE! youtube data has loaded")
        self.__save_merged_datum()


    def __filter_youtube_basic_info(self) -> None:
        pass

    def __complement_youtube_basic_info(self) -> None:
        # youtube の基本情報を揃える
        ## vpost と youtube search とで足りないもの違うと思うから分けてやる
        pass

    def __collect_youtube_data(self) -> None:
        self.logger.info("prepare to collect youtube video data")
        # 動画リスト取得
        target_videos = list(map(
            lambda x: x.youtube.channel_id,
            filter(
                lambda x: (not tried_to_get_self_intro_video(x)) and got_upload_lists,
                self.vtuber_merged_datum.values()
            )
        ))[:3]
        self.logger.info(f"will try to get {len(target_videos)} upload video lists")


        upload_video_lists = self.youtube_collector.get_upload_video_lists(target_videos)
        for key, upload_list in upload_video_lists.items():
            self.vtuber_merged_datum[key].youtube.upload_videos = upload_list
            self.vtuber_merged_datum[key].youtube.video_count_n = len(upload_list)

        self.logger.info(f"DONE! GOT {len(upload_video_lists)} upload video lists")

        # 自己紹介動画抽出

        self.__save_merged_datum()

    def __filter_youtube_content_info(self) -> None:
        pass

    def __collect_twitter_data(self) -> None:
        ### データを埋める処理は個別でやるんじゃなくて、一旦キューに入れてあとでまとめてやるほうがいい？
        ## Twitter id 分かってないやつは，youtube のチャンネルページからURL引っこ抜け
        ### チャンネルページのリンク欄は API で取得できないぜ!
        ## チャンネルの概要欄から Twitter id 引っこ抜け
        ## チャンネル名 を Twitter で検索かけてそれっぽいアカウント引っこ抜け
        pass

    def __filter_all_data(self) -> None:
        pass

    def __save_merged_datum(self) -> None:
        save_vtuber_merged_datum(self.vtuber_merged_datum.values(), self.merged_json_path)
        self.logger.info(f"saved merged datum to {self.merged_json_path}")

    def __output_dataset(self) -> None:
        pass

