import re
import logging

from dataset_for_annotator.data_types import MissingValue, TwitterData, VTuberMergedData

TWITTER_URL_PATTERN = re.compile(r"https://twitter.com/([\w]+)")
def extract_twitter_id(target: str) -> str | None:
    # 最初に見つかった twitter id を返す. ママの id など複数掲載されていた場合は考慮しない
    # 余裕があれば Twitter: @hogehoge みたいなパターンにも対応する
    match = TWITTER_URL_PATTERN.findall(target)
    if not match:
        return None

    return match[0][1]

class TwitterCollector:
    def __init__(self, twitter_api_key: str, logger: logging.Logger) -> None:
        self.logger = logger
        twitter = None


    @classmethod
    def extract_twitter_account(cls, target: VTuberMergedData) -> TwitterData | MissingValue:
        # YouTube のリンク(バナー横やチャンネル概要欄のさらに下にあるもの)が取得できないので頑張る

        # 自己紹介動画あるならそれ使う
        if target.target_video.description:
            twitter_id = extract_twitter_id(target.target_video.description)
            if twitter_id:
                return TwitterData(twitter_id)

        # YouTube の概要欄を検索
        if target.youtube.channel_description:
            twitter_id = extract_twitter_id(target.youtube.channel_description)
            if twitter_id:
                return TwitterData(twitter_id)

        return MissingValue.NotFound

    def search_twitter_id(target: VTuberMergedData) -> str:
        # Twitter の検索でアカウントを見つける
        ## YouTube のチャンネルから日本語を抜き出す
        ## その名前で"名前hoge"で検索
        ## 一番上に出てきたツイートの投稿者……かな多分
        raise Exception("not implement")

    def get_and_set_twitter_info(self, target: VTuberMergedData) -> None:
        target.twitter.twitter_id
        # Twitter の情報を取得する

        # Twitter の情報セット
        raise Exception("not implement")
