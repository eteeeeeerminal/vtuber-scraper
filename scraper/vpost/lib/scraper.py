from dataclasses import replace
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

from .vtuber_data import VTuberData, load_vtuber_datum, save_vtuber_datum

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


class VTuberListScraper:

    SAVE_PERIOD = 10
    ITEM_LIMIT = 100
    OLDEST_FIRST = 2

    def __init__(self, save_dir: str) -> None:
        self.save_dir = pathlib.Path(save_dir)
        self.state_json_path = self.save_dir.joinpath("state.json")
        self.vtuber_data_json_path = self.save_dir.joinpath("vtuber_data.json")

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
    def __init__(self) -> None:
        pass
