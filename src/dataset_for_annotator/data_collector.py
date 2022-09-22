"""欠けているデータなんかを集めてくる部分
"""

import logging
from typing import Iterable

from apiclient import discovery

from dataset_for_annotator.data_filter import got_upload_lists, is_self_intro_video

from .data_types import MissingValue, VTuberMergedData, YouTubeVideoData
from youtube.youtube_data import str_to_datetime

class TwitterCollector:
    def __init__(self) -> None:
        pass

    def find_twitter_id(target: VTuberMergedData) -> str:
        # YouTube のリンク(バナー横やチャンネル概要欄のさらに下にあるもの)が取得できないので頑張る

        # YouTube の概要欄から Twitter アカウントを発見
        ## ママ上のアカウントを載せてる人もいるので注意, 複数Twitterアカウント載せてる人は飛ばすか, 最初の人を採用かも
        ## ママ上のアカウントのみある場合とかは知らない知らない
        ## 正規表現で id 抽出

        # Twitter 検索で見つける
        ## YouTube のチャンネルから日本語を抜き出す
        ## その名前で"名前hoge"で検索
        ## 一番上に出てきたツイートの投稿者……かな多分
        pass


def user_id_to_upload_list_id(user_id: str) -> str:
    # 勘で変換してるだけなので, 今後使えなくなるかも
    # 使えなくなった場合は, API でチャンネルの ContentDetails とかを叩くこと

    # channel id は 先頭がUC
    # アップロード済みの再生リストは, 先頭がUUそれ以外は channel id と一致
    if user_id[:2] == "UC":
        user_id = list(user_id)
        user_id[1] = "U"
        user_id = "".join(user_id)
    elif user_id[:2] == "UU":
        pass
    else:
        return None

    return user_id

def response_to_video_data(response: dict) -> YouTubeVideoData:
    return YouTubeVideoData(
        response["snippet"]["resourceId"]["videoId"],
        response["snippet"]["title"],
        response["snippet"]["description"],
        str_to_datetime(response["snippet"]["publishedAt"])
    )

def response_to_video_list(response: list) -> list[YouTubeVideoData]:
    return list(map(response_to_video_data, response))

def extract_self_intro_video(target: VTuberMergedData) -> MissingValue | YouTubeVideoData:
    """target の投稿動画一覧から, 自己紹介動画を抽出"""
    if target.youtube.upload_videos is None:
        return MissingValue.Unacquired

    self_intro_videos: filter[YouTubeVideoData] = filter(is_self_intro_video, target.youtube.upload_videos)
    for video in self_intro_videos:
        return video

    if got_upload_lists(target):
        return MissingValue.NotExist

    else:
        return MissingValue.NotFound

class YouTubeCollector:
    def __init__(self, api_key: str, logger: logging.Logger) -> None:
        self.youtube = discovery.build('youtube', 'v3', developerKey=api_key)

        self.logger = logger

    def get_upload_video_lists(self, youtube_ids: Iterable[str]) -> dict[str, list[YouTubeVideoData]]:
        """指定されたチャンネルの投稿動画リストを取得"""

        upload_list_ids = map(user_id_to_upload_list_id, youtube_ids)
        max_result = 50
        upload_list_dict: dict[str, dict] = {}

        for list_id, channel_id in zip(upload_list_ids, youtube_ids):
            self.logger.debug(f"get {channel_id}'s upload list")
            request = self.youtube.playlistItems().list(
                part="snippet",
                maxResults=max_result,
                playlistId=list_id,
                fields="nextPageToken,items/snippet(publishedAt,title,description,resourceId/videoId)"
            )

            upload_videos = []
            while request:
                response = request.execute()
                upload_videos.extend(response_to_video_list(response["items"]))
                request = self.youtube.playlistItems().list_next(request, response)

            upload_list_dict[channel_id] = upload_videos

        return upload_list_dict

    def set_self_intro_video(self, target: VTuberMergedData) -> None:
        """target の投稿動画一覧から, 自己紹介動画を抽出"""
        target.target_video = extract_self_intro_video(target)
        if not isinstance(target.target_video, MissingValue):
            self.logger.debug(f"found self-intro video {target.target_video.title}:{target.target_video.video_id}")
