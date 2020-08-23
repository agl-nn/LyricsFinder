import requests
from pprint import pprint
from bs4 import BeautifulSoup
import re

BASE_URL = 'https://api.genius.com/'


class LyricsFinder:
    def __init__(self, token):
        self.genius_oauth = token

    def get_lyrics_url(self, artist, track):
        """
        метод ищет на сайте genius.com трек track у автора artist
        возвращает ссылку на страницу для парсинга текста
        """
        url = BASE_URL + 'search'
        params = {'access_token': self.genius_oauth, 'q': track}
        r = requests.get(url, params=params)
        if not r.ok:
            raise Exception(f'Something went wrong! Error code: {r.status_code}')
        search_result = r.json()['response']['hits']
        for item in search_result:
            artist_name = item['result']['primary_artist']['name']
            lyrics_url = item['result']['url']
            if artist.lower().strip() == artist_name.lower():
                return lyrics_url

    def get_lyrics(self, artist, track):
        """
        метод парсит страницу, полученную с помощью get_lyrics_url
        возвращает текст песни
        """
        url = self.get_lyrics_url(artist, track)
        if not url:
            raise Exception('failed to get url on request')
        # пишем рягулярное выражение для поиска текста в html:
        pattern = re.compile(url[18:] + r'#note-\d')
        post_page = requests.get(url)
        soup = BeautifulSoup(post_page.text, 'html.parser')
        text = soup.find_all(href=pattern)
        return [string.text for string in text]


if __name__ == '__main__':
    TOKEN = ''
    finder = LyricsFinder(TOKEN)
    lyrics = finder.get_lyrics('nirvana', 'come as you are')
    pprint(lyrics)
