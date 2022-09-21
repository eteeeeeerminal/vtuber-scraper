"""
データセットに入れるデータを決める
"""

from typing import Callable
from collections.abc import Iterable

from .data_types import MissingValue, VTuberMergedData, YouTubeVideoData

FilterFunc = Callable[[VTuberMergedData], bool]

# twitter からのデータに関する条件
def has_twitter(target: VTuberMergedData) -> bool:
    return target.twitter is None

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
    return target.youtube.video_count_n <= len(target.youtube.upload_videos)

def too_few_uploads(target: VTuberMergedData) -> bool:
    pass

def too_few_views(target: VTuberMergedData) -> bool:
    pass

youtube_basic_filter_conds: tuple[FilterFunc] = (
)
"""YouTube の動画情報を取得するかどうか判定
データの補完前にも実行するので, 欠損値があった場合は弾かない
"""

youtube_uploads_filter_conds: tuple[FilterFunc] = (
    found_self_intro_video,
)
"""YouTube の情報を一通り取得できた後のフィルター
"""

youtube_filter_conds: tuple[FilterFunc] = youtube_basic_filter_conds + youtube_uploads_filter_conds


all_filter_conditions: tuple[FilterFunc] = youtube_filter_conds + twitter_filter_conds

def adopt_filters(filter_conditions: tuple[FilterFunc], target: Iterable[VTuberMergedData]) -> Iterable[VTuberMergedData]:
    """target に filter_conditions で渡した条件を全て適用してフィルターする"""
    # なんとなくまだ早くできそう
    for cond in filter_conditions:
        target = filter(cond, target)

    return target


# その他のフィルター
def is_self_intro_video(video: YouTubeVideoData) -> bool:
    pass
