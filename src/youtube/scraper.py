import json
import os
import pathlib
import datetime
from re import search

from apiclient import discovery

from .youtube_data import SearchResult, SearchResultItem, load_search_datum, save_search_datum

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

class YouTubeSearchScraper:
    """youtube の検索結果を保存"""
    def __init__(self, save_dir: str, api_key: str, ng_words: list[str]) -> None:
        self.save_dir = pathlib.Path(save_dir)
        self.save_path = self.save_dir.joinpath("search_result.json")

        self.youtube = discovery.build('youtube', 'v3', developerKey=api_key)

        self.ng_words = ng_words

        self.search_results: list[SearchResult] = []
        if os.path.exists(self.save_path):
            with open(self.save_path, "r", encoding="utf-8") as f:
                result_json = json.load(f)
                self.search_results = load_search_datum(result_json)


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
            search_result.items.append([response_to_item(r) for r in response["items"]])
            request = self.youtube.search().list_next(request, response)
            i += 1

        self.search_results.append(search_result)
        self.__save()

    def __save(self) -> None:
        os.makedirs(self.save_dir, exist_ok=True)
        save_search_datum(self.search_results, self.save_path)

class YTChannelScraper:
    """ vpost で取得できていない分の VTuber のチャンネルの情報を取得"""
    def __init__(self, save_dir: str, vpost_data_path: str) -> None:
        pass

    def scrape(self) -> None:
        # vpost に含まれていたらスキップ
        # チャンネルデータを保存
        pass