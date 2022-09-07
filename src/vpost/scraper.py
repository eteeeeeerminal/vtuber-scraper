import os
import pathlib
import json
import re
import time

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from .vtuber_data import VTuberData, load_detail_datum, load_vtuber_datum, save_vtuber_datum, VTuberDetails, VideoData, save_detail_datum

VTUBER_DATABASE_URL = "https://vtuber-post.com/database/index.php"

def VTuber_detail_url(youtube_id: str) -> str:
    return f"https://vtuber-post.com/database/detail.php?id={youtube_id}"

def get_web_driver() -> webdriver.Chrome:
    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

def element_to_vtuber_data(web_element: WebElement) -> VTuberData:
    name = web_element.find_element(by=By.CLASS_NAME, value="name").text

    youtube_info = web_element.find_element(by=By.CLASS_NAME, value="channel")
    youtube_link = youtube_info.find_element(by=By.TAG_NAME, value="a").get_attribute("href")
    match = re.search(r"channel/([\d\w-]+)", youtube_link)
    youtube_id = match.groups()[0]

    registrants_n = web_element.find_element(by=By.CLASS_NAME, value="regist").text
    play_times = web_element.find_element(by=By.CLASS_NAME, value="play").text
    upload_videos = web_element.find_element(by=By.CLASS_NAME, value="upload").text

    group_name = web_element.find_element(by=By.CLASS_NAME, value="group").text

    return VTuberData(
        name=name,

        youtube_id=youtube_id,

        registrants_n=int(registrants_n.replace("人", "").replace(",", "")),
        play_times=int(play_times.replace("回", "").replace(",", "")),
        upload_videos=int(upload_videos.replace("本", "").replace(",", "")),

        group_name=group_name,
    )

def element_to_videodata(web_element: WebElement) -> VideoData:
    title_elm = web_element.find_element(by=By.CLASS_NAME, value="title")
    title_elm = title_elm.find_element(by=By.TAG_NAME, value="a")
    video_id = title_elm.get_attribute("videoid")
    title = title_elm.text
    timestamp = web_element.find_element(by=By.CLASS_NAME, value="time").text
    view_n = web_element.find_element(by=By.CLASS_NAME, value="play").text
    good = web_element.find_element(by=By.CLASS_NAME, value="eval").text

    try:
        # timestamp をよしなに変換する処理を from_json にしか作ってないのでとりあえず
        return VideoData.from_json({
            "video_id": video_id,
            "title": title,
            "timestamp": timestamp,
            "view_n": int(view_n.replace("回", "").replace(",", "")),
            "good": int(good.replace(",", "")),
        })
    except:
        # timestamp が壊れてるデータがあるとエラーになる
        # 面倒くさいので、フォーマットが乱れてるデータは無視
        return None



STATE_DATA_FILE_NAME = "state.json"
VTUBER_DATA_FILE_NAME = "vtuber_data.json"
DETAIL_DATA_FILE_NAME = "detail_data.json"

class VTuberListScraper:

    SAVE_PERIOD = 10
    ITEM_LIMIT = 100
    OLDEST_FIRST = 2

    def __init__(self, save_dir: str) -> None:
        self.save_dir = pathlib.Path(save_dir)
        self.state_json_path = self.save_dir.joinpath(STATE_DATA_FILE_NAME)
        self.vtuber_data_json_path = self.save_dir.joinpath(VTUBER_DATA_FILE_NAME)

        self.web_driver = get_web_driver()
        self.vtuber_datum: list[VTuberData] = []

    def __load_state(self) -> None:
        if os.path.exists(self.state_json_path):
            with open(self.state_json_path, "r", encoding="utf-8") as f:
                state_dict = json.load(f)

            assert self.__jump_page(state_dict["page_num"])

    def __get_current_page_num(self) -> int:
        pagination = self.web_driver.find_element(by=By.CLASS_NAME, value="now")
        return int(pagination.text)

    def __set_search_cond(self) -> None:
        limit_select = self.web_driver.find_element(by=By.NAME, value="limit")
        limit_select = Select(limit_select)
        limit_select.select_by_value(str(self.ITEM_LIMIT))

        order_select = self.web_driver.find_element(by=By.NAME, value="order")
        order_select = Select(order_select)
        order_select.select_by_value(str(self.OLDEST_FIRST))

        non_movie_check = self.web_driver.find_element(by=By.NAME, value="non_movie")
        non_movie = non_movie_check.get_attribute("value")
        if non_movie != 1:
            non_movie_check.click()

        submit_button = self.web_driver.find_element(by=By.ID, value="search_submit")
        submit_button.click()

        time.sleep(3)

    def __extract_page_num(self, link: WebElement) -> int|None:
        html = link.get_attribute("outerHTML")
        match = re.search(r"FormSubmit\(([\d]+)\)", html)
        if not match:
            return None
        return int(match.groups()[0]) +1

    def __jump_page(self, target_page_num: int) -> bool:
        previous_link = 0
        while self.__get_current_page_num() != previous_link:
            if self.__get_current_page_num() == target_page_num:
                return True

            pagenation = self.web_driver.find_element(by=By.CLASS_NAME, value="pagenation")
            page_links = pagenation.find_elements(by=By.TAG_NAME, value="a")
            link_tuples = [(self.__extract_page_num(link), link) for link in page_links]

            previous_link = self.__get_current_page_num()

            time.sleep(1.2)
            if target_page_num < link_tuples[0][0]:
                # 目的のページを過ぎてるから戻る
                link_tuples[0][1].click()

            elif target_page_num > link_tuples[-1][0]:
                # 目的のページはまだ先
                link_tuples[-1][1].click()

            else:
                for page_num, link in link_tuples:
                    if page_num == target_page_num:
                        link.click()
                        break

        return False

    def ready_scraper(self) -> None:
        self.web_driver.get(VTUBER_DATABASE_URL)
        time.sleep(3)

        self.__set_search_cond()
        if os.path.exists(self.vtuber_data_json_path):
            self.vtuber_datum = load_vtuber_datum(self.vtuber_data_json_path)
        self.__load_state()

    def __scrape_page(self) -> None:
        vtuber_list = self.web_driver.find_element(by=By.CLASS_NAME, value="vtuber_list")
        vtuber_elms = vtuber_list.find_elements(by=By.CLASS_NAME, value="clearfix")
        self.vtuber_datum.extend(map(element_to_vtuber_data, vtuber_elms))

    def scrape_vtuber_list(self) -> None:
        i = 0
        while True:
            i += 1
            if i % self.SAVE_PERIOD == 0:
                self.save()

            self.__scrape_page()
            if not self.__jump_page(self.__get_current_page_num()+1):
                # 次のページに飛べなかったら終了
                break

        self.save()

    def save(self) -> None:
        os.makedirs(self.save_dir, exist_ok=True)

        with open(self.state_json_path, "w", encoding="utf-8") as f:
            json.dump({"page_num": self.__get_current_page_num()}, f)

        save_vtuber_datum(self.vtuber_datum, self.vtuber_data_json_path)

    def __del__(self):
        self.web_driver.quit()

class VTuberDetailScraper:

    SAVE_PERIOD = 10

    def __init__(self, save_dir: str) -> None:
        self.save_dir = pathlib.Path(save_dir)
        self.detail_data_json_path = self.save_dir.joinpath(DETAIL_DATA_FILE_NAME)
        self.vtuber_data_json_path = self.save_dir.joinpath(VTUBER_DATA_FILE_NAME)

        self.web_driver = get_web_driver()
        if os.path.exists(self.detail_data_json_path):
            detail_list = load_detail_datum(self.detail_data_json_path)
            self.detail_dict: dict = {d.youtube_id :d for d in detail_list}
        else:
            self.detail_dict: dict = {}
        self.vtuber_datum = load_vtuber_datum(self.vtuber_data_json_path)

    def __scrape_page(self, youtube_id: str) -> VTuberDetails:
        self.web_driver.get(VTuber_detail_url(youtube_id))

        description = self.web_driver.find_element(by=By.CLASS_NAME, value="desc").text

        twitter_id = None
        link_elms = self.web_driver.find_elements(by=By.CLASS_NAME, value="group")
        for link_elm in link_elms:
            if "Twitter" in link_elm.text and "@" in link_elm.text:
                twitter_id = link_elm.find_element(by=By.TAG_NAME, value="a").text

        # video data
        movie_list_elms = self.web_driver.find_elements(by=By.CLASS_NAME, value="movie_list")
        video_elms = [elms.find_elements(by=By.CLASS_NAME, value="clearfix") for elms in movie_list_elms]
        video_list = [list(map(lambda elm: element_to_videodata(elm), elm_list)) for elm_list in video_elms]
        video_list = sum(video_list, [])
        video_list = list(filter(lambda x: x is not None, video_list))

        time.sleep(3)
        return VTuberDetails(
            youtube_id=youtube_id,
            description=description,
            twitter_id=twitter_id,
            recent_videos=video_list
        )

    def scrape_youtube_datum(self) -> None:
        for i, value in enumerate(self.vtuber_datum):
            print(value.name)
            # 動画の数が少ないのはデビュー直後 or 引退済み
            if not value.upload_videos or value.upload_videos < 5:
                continue

            # 取得済みはスキップ
            if value.youtube_id in self.detail_dict.keys():
                continue

            if i and i % self.SAVE_PERIOD == 0:
                self.save()

            youtube_id = value.youtube_id
            if youtube_id:
                try:
                    yt_data = self.__scrape_page(youtube_id)
                    self.detail_dict[youtube_id] = yt_data
                except:
                    print(f"errror at {value.name}")

        self.save()

    def save(self) -> None:
        os.makedirs(self.save_dir, exist_ok=True)
        detail_datum = self.detail_dict.values()
        save_detail_datum(detail_datum, self.detail_data_json_path)

    def __del__(self):
        self.web_driver.quit()
