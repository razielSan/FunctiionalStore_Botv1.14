from typing import Dict, List


class YoutubeSearchApi:
    async def get_description_video_by_youtube(
        self,
        response_youtube: List[Dict],
        youtube_video_url: str,
        youtube_channel_url: str,
    ) -> List[str]:
        """
        Формирует описание для видео из youtube.

        Работает с сайтом https://www.youtube.com/

        Args:
            response_youtube (List[Dict]): Список содержащий словари с данными видео
            ютуба.
            youtube_video_url (str): URL для формирования ссылки на видео
            youtube_channel_url (str): URL для формирования ссылки на канал

        Returns:
            List[str]: Список содержащий строки с описанием ютуб видео
        """

        array_video_description: List = []
        order: int = 0
        # Проходимся по списку с ответами для youtube
        for result in response_youtube:
            order += 1  # Номер описания видео
            video_id: str = result["id"].get("videoId", None)
            channel_id: str = result["id"].get("channelId", None)

            if video_id:
                url: str = youtube_video_url.format(video_id=video_id)
                template: str = f"Ссылка на видео\n{url}"

            else:
                url: str = youtube_channel_url.format(channel_id=channel_id)
                template: str = f"Ссылка на канал\n{url}"

            # Формируем описание для видео
            title: str = result["snippet"]["title"].replace("&quot;", " ")
            description: str = result["snippet"]["description"].replace("&quot;", " ")

            array_video_description.append(
                f"{order}. {title}\n\n{description}\n\n{template}\n"
            )
        return array_video_description


search_youtube_api: YoutubeSearchApi = YoutubeSearchApi()
