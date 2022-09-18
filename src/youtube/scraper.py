import os
import pathlib
import datetime
from apiclient import discovery

from .youtube_data import SearchResult, SearchResultItem, YouTubeChannelData, load_search_datum, save_search_datum, load_channel_datum, save_channel_datum
from vpost.vtuber_data import VTuberDetails, load_detail_datum

def response_to_item(response: dict) -> SearchResultItem:
    print(response)
    return SearchResultItem(
        kind = response["id"]["kind"].replace("youtube", ""),
        video_id = response["id"]["videoId"],
        publish_time = response["snippet"]["publishedAt"],
        channel_id = response["snippet"]["channelId"],
        channel_title = response["snippet"]["channelTitle"],
        title = response["snippet"]["title"],
        description = response["snippet"]["description"]
    )

SEARCH_RESULT_JSON_NAME = "search_result.json"

class YouTubeSearchScraper:
    """youtube の検索結果を保存"""
    def __init__(self, save_dir: str, api_key: str, ng_words: list[str]) -> None:
        self.save_dir = pathlib.Path(save_dir)
        self.save_path = self.save_dir.joinpath(SEARCH_RESULT_JSON_NAME)

        self.youtube = discovery.build('youtube', 'v3', developerKey=api_key)

        self.ng_words = ng_words

        self.search_results: list[SearchResult] = []
        if os.path.exists(self.save_path):
            self.search_results = load_search_datum(self.save_path)


    def search(self, query, order="rating", max_page=20) -> None:
        query += " -" + " -".join(self.ng_words)

        id_fields = "id(kind,videoId)"
        snippet_fields = "snippet(publishedAt,channelId,title,description,channelTitle)"

        request = self.youtube.search().list(
            part="id,snippet",
            maxResults=50,
            type="video",
            order=order,
            q=query,
            fields=f"nextPageToken,items({id_fields},{snippet_fields})"
        )
        search_result = SearchResult(
            timestamp = datetime.datetime.now(),
            query = query,
            order = order,
            items = []
        )

        i = 0
        while request and i < max_page:
            response = request.execute()
            search_result.items.extend([response_to_item(r) for r in response["items"]])
            request = self.youtube.search().list_next(request, response)
            i += 1

        self.search_results.append(search_result)
        self.__save()

    def __save(self) -> None:
        os.makedirs(self.save_dir, exist_ok=True)
        save_search_datum(self.search_results, self.save_path)


def response_to_channel_data(response: dict) -> YouTubeChannelData:
    print(response)
    return YouTubeChannelData(
        channel_id = response["id"],
        title = response["snippet"]["title"],
        description = response["snippet"]["description"],
        publish_time = response["snippet"]["publishedAt"],
        upload_list_id = response["contentDetails"]["relatedPlaylists"]["uploads"],
        view_count = response["statistics"]["viewCount"],
        subscriber_count = response["statistics"].get("subscriberCount", None),
        video_count = response["statistics"]["videoCount"]
    )

class YouTubeChannelScraper:
    """ vpost で取得できていない分の VTuber のチャンネルの情報を取得"""
    def __init__(self, save_dir: str, api_key: str, vpost_data_path: str) -> None:
        """
        Args:
            save_dir (str): 保存先のディレクトリ. 取得対象の channel id も `save_dir/search_result.json` から取得.
            api_key (str): YouTube Data API の api key
            vpost_data_path (str): `vpost_data_path` 以下にすでに保存済みのチャンネルは取得しない.
        """
        self.save_dir = pathlib.Path(save_dir)
        self.save_path = self.save_dir.joinpath("channels.json")
        self.result_path = self.save_dir.joinpath(SEARCH_RESULT_JSON_NAME)

        self.youtube = discovery.build('youtube', 'v3', developerKey=api_key)

        self.yt_search_list: list[SearchResult] = load_search_datum(self.result_path)
        self.vtuber_details: list[VTuberDetails] = load_detail_datum(vpost_data_path)
        self.vtuber_channel_data: list[YouTubeChannelData] = []

        self.__extract_target()

    def __extract_target(self) -> None:
        self.target: dict[str, SearchResultItem] = {}
        detailed_ids: set[str] = set(map(lambda x: x.youtube_id, self.vtuber_details))
        for search_result in self.yt_search_list:
            for item in search_result.items:
                if item.channel_id in detailed_ids:
                    continue

                if item.channel_id in self.target:
                    continue

                self.target[item.channel_id] = item

        print(f"target num is {len(self.target)}")

    def scrape(self) -> None:
        target_channels = list(self.target.keys())
        divide_n = 50
        part_n = int(len(target_channels) / divide_n)
        subdivided_targets = [target_channels[divide_n*i: divide_n*(i+1)] for i in range(part_n)]

        snippet_fields = "snippet(title,description,publishedAt)"
        content_details_fields = "contentDetails/relatedPlaylists/uploads"
        statistics_fields = "statistics(viewCount,subscriberCount,hiddenSubscriberCount,videoCount)"

        for targets in subdivided_targets:
            request = self.youtube.channels().list(
                part="id,snippet,contentDetails,statistics",
                id=','.join(targets),
                maxResults=50,
                fields=f"nextPageToken,items(id,{snippet_fields},{content_details_fields},{statistics_fields})"
            )

            while request:
                response = request.execute()
                self.vtuber_channel_data.extend([response_to_channel_data(r) for r in response["items"]])
                request = self.youtube.search().list_next(request, response)

        self.__save()

    def __save(self) -> None:
        os.makedirs(self.save_dir, exist_ok=True)
        save_channel_datum(self.vtuber_channel_data, self.save_path)


