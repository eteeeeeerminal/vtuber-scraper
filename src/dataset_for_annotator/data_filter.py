"""
データセットに入れるデータを決める
"""

import re
from typing import Callable
from collections.abc import Iterable

from .data_types.common import MissingValue
from .data_types.merged import TwitterData, YouTubeVideoData, VTuberMergedData

FilterFunc = Callable[[VTuberMergedData], bool]

# twitter からのデータに関する条件
def has_twitter(target: VTuberMergedData) -> bool:
    return isinstance(target.twitter, TwitterData)

def has_twitter_detail(target: VTuberMergedData) -> bool:
    if not isinstance(target.twitter, TwitterData):
        return False
    return bool(target.twitter.name)

def tried_to_get_twitter_id(target: VTuberMergedData) -> bool:
    if isinstance(target.twitter, TwitterData):
        return True

    if target.twitter == MissingValue.NotExist:
        return True

    return False

twitter_filter_conds: tuple[FilterFunc] = (
    has_twitter,
)

# YouTube からのデータに関する条件

## 多分 Twitter 持ってる VTuber で自己紹介動画投稿してたら日本語話してるので省略
### def is_jp(target: VTuberMergedData) -> bool:

def found_self_intro_video(target: VTuberMergedData) -> bool:
    return isinstance(target.target_video, YouTubeVideoData)

def tried_to_get_self_intro_video(target: VTuberMergedData) -> bool:
    return found_self_intro_video(target) or target.target_video == MissingValue.NotExist

def got_upload_lists(target: VTuberMergedData) -> bool:
    if target.youtube.video_count_n is None or target.youtube.got_video_n is None:
        return False

    return target.youtube.video_count_n <= target.youtube.got_video_n

## チャンネル説明欄に書いてなくても自己紹介動画の方に説明があるかも
### def exist_channel_description(target: VTuberMergedData) -> bool:
###    return target.youtube.channel_description

def ng_words_filter(target: VTuberMergedData) -> bool:
    description_ng_words = (
        "コンドーム",  # 公式アンバサダーがいたので
    )
    description_ng_words = list(map(re.compile, description_ng_words))

    title_ng_words = (
        "切り抜き",
    )
    title_ng_patterns = list(map(re.compile, title_ng_words)) + description_ng_words

    if any(map(lambda x: x.search(target.youtube.name), title_ng_patterns)):
        return False

    description = target.youtube.channel_description
    if description and any(map(lambda x: x.search(description), description_ng_words)):
        return False

    return True

def enough_uploads(target: VTuberMergedData) -> bool:
    return target.youtube.video_count_n is None \
        or target.youtube.video_count_n > 3

def enough_few_views(target: VTuberMergedData) -> bool:
    return target.youtube.view_count is None \
        or target.youtube.view_count > 10

def enough_subscriber_count(target: VTuberMergedData) -> bool:
    return target.youtube.subscriber_count is None \
        or target.youtube.subscriber_count > 5

youtube_basic_filter_conds: tuple[FilterFunc] = (
    ng_words_filter,
    enough_uploads,
    enough_few_views, enough_subscriber_count,
)
"""YouTube の動画情報を取得するかどうか判定
データの補完前にも実行するので, 欠損値があった場合は弾かない
"""

youtube_content_filter_conds: tuple[FilterFunc] = (
    found_self_intro_video,
)
"""YouTube の情報を一通り取得できた後のフィルター
"""

youtube_filter_conds: tuple[FilterFunc] = youtube_basic_filter_conds + youtube_content_filter_conds


all_filter_conditions: tuple[FilterFunc] = youtube_filter_conds # + twitter_filter_conds

def adopt_filters(filter_conditions: tuple[FilterFunc], target: Iterable[VTuberMergedData]) -> Iterable[VTuberMergedData]:
    """target に filter_conditions で渡した条件を全て適用してフィルターする"""
    # なんとなくまだ早くできそう
    for cond in filter_conditions:
        target = filter(cond, target)

    return target


# その他のフィルター
def is_self_intro_video(video: YouTubeVideoData) -> bool:
    # nice_to_meet_you = re.compile("はじめまして")
    ## ノイズが多かったので一旦除外
    self_intro = re.compile("自己紹介")
    clip = re.compile("切り抜き")
    live = re.compile("配信")
    colab = re.compile("コラボ")
    ng_patterns = (
        "生放送アーカイブ",
        "エイプリルフール", "2人組", "ふたりで",
        "#shorts", "Shorts", # shorts 動画は縦長でアス比が合わせにくいので除外
        "記念枠", "雑談", "Apex 練習", # 配信は長いので除外
        "100の質問", "1キル1答", "100個の質問", "【龍玉寺或斗】", "【 Dead by Daylight 】", # 長い
        "英語で", "歌曲", "自我介绍", "Español", "韓国語で", "【Дебют】", # 日本語じゃなかったりするので除外
        "自己紹介メイキング", "今日のおすすめキャスト", "#コミケ", "自己紹介動画を見る", "ツイステ",
        "一問一答", # 企画の影響が強すぎて個性が出ないので除外
        "赤城まやの自己紹介と質問箱返信！", "【動画撮影】", "【スタマス】", "りりてれ", "リトルナイトメアやってみた", # 長い
        "シルエット自己紹介動画", "『自己紹介動画』あるある", "アイドル風自己紹介動画選手権"
    )
    ng_patterns = list(map(re.compile, ng_patterns))

    ng_patterns_in_description = (
        "#vtuber一問一答自己紹介",
        "【Self-Introduction】", # 英語率高い
    )
    ng_patterns_in_description = list(map(re.compile, ng_patterns_in_description))

    if any(map(lambda x: x.search(video.title), ng_patterns)):
        # 1つでも ng ワードがあれば除外
        return False

    if video.description:
        if any(map(lambda x: x.search(video.description), ng_patterns_in_description)):
            # 1つでも ng ワードがあれば除外
            return False

    if colab.search(video.title) or (video.description and colab.search(video.description)):
        # コラボは除外
        return False

    if live.search(video.title) and not clip.search(video.title):
        # 切り抜きじゃない配信アーカイブの場合, 長いので除外
        return False

    if self_intro.search(video.title):
        # 自己紹介動画
        return True

    return False

