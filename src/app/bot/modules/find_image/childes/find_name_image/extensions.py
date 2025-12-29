from pathlib import Path

from icrawler.builtin import BingImageCrawler
from icrawler.downloader import ImageDownloader
from googleapiclient.discovery import build


class CustomDownloader(ImageDownloader):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }


class Crawler:
    def __init__(
        self,
        path: Path,
        feel_threads: int = 1,
        parser_threads: int = 1,
        downloader_threads: int = 4,
    ):
        self.feel_threads = feel_threads
        self.parser_threads = parser_threads
        self.downloader_threads = downloader_threads
        self.path = path

    def get_bing_image_crawler(self):
        return BingImageCrawler(
            feeder_threads=self.feel_threads,  # Увеличиваем feeder
            parser_threads=self.parser_threads,  # Увеличиваем parser
            downloader_threads=self.downloader_threads,  # Максимальное количество потоков загрузки
            storage={"root_dir": self.path},
            downloader_cls=CustomDownloader,
        )


class Google:
    def __init__(
        self,
        query: str,
        api_key: str,
        cx: str,
    ):
        self.query = query
        self.api_key = api_key
        self.cx = cx

    def search_with_google_client(self):
        service = build("customsearch", "v1", developerKey=self.api_key)
        res = service.cse().list(q=self.query, cx=self.cx, searchType="image").execute()
        return res.get("items", [])
