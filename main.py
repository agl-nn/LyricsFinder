import requests
from bs4 import BeautifulSoup
import os
from typing import Optional
from collections import namedtuple

BASE_URL = 'https://api.genius.com/'


class LyricsFinder:
    def __init__(self, token: str):
        self.genius_oauth = token
        self.lyrics_dir = os.path.join(os.getcwd(), 'lyrics' + os.sep)

    def get_lyrics_url(self, artist: str, track: str) -> str:
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
            if artist.lower().strip() in artist_name.lower():
                return lyrics_url

    def get_lyrics_by_url(self, artist: str, track: str) -> namedtuple:
        """
        метод парсит страницу, полученную с помощью get_lyrics_url
        возвращает текст песни
        """
        url = self.get_lyrics_url(artist, track)
        if not url:
            raise Exception('failed to get url on request')
        while True:
            post_page = requests.get(url)
            soup = BeautifulSoup(post_page.content, 'html.parser')
            lyrics = soup.find_all('div', class_='lyrics')
            if len(lyrics) != 0:
                break
        parsed_lyrics = lyrics[0].text
        Lyrics = namedtuple('Lyrics', ['artist', 'track', 'lyrics'])
        lyrics = Lyrics(artist, track, parsed_lyrics)
        return lyrics

    def write_lyrics_to_txt(self, lyrics: namedtuple):
        """
        пишет текст песни в файл
        """
        artist = lyrics.artist.title()
        track = lyrics.track.title()
        print('from namedtuple', artist, track)
        # папка с текстами исполнителя artist в папке self.lyrics_dir:
        artist_dir = os.path.join(self.lyrics_dir, artist)
        # если папки artist_dir не существует - создаём её и сохраняем все тексты исполонителя туда:
        if artist not in os.listdir(self.lyrics_dir) and not os.path.isdir(artist_dir):
            os.mkdir(artist_dir)
        with open(f'{artist_dir}{os.sep}{track}.txt', 'w', encoding='utf=8') as f:
            f.write(f'{artist} -- {track}')
            for line in lyrics.lyrics:
                f.write(line)

    def get_lyrics_from_txt(self, artist: str, track: str) -> Optional[str]:
        """
        метод ищет и возвращает текст запрашиваемого трека в папке исполнителя artist_dir
        если документа с треком в папке нет, возвращает None
        """
        file_name = f'{artist.title()} -- {track.title()}.txt'
        artist_dir = os.path.join(self.lyrics_dir, artist).title()
        if artist_dir in self.lyrics_dir and file_name in os.listdir(artist_dir):
            with open(f'{artist_dir + os.sep}{file_name}', 'r', encoding='utf-8') as f:
                lyrics = f.read()
            return lyrics
        else:
            return None

    def get_lyrics(self, artist: str, track: str) -> str:
        """
        метод принимает на вход название исполнителя и трека для поиска.
        если искомый текст нельзя найти в файле с помощью метода get_lyrics_from_txt
        парсит его с get_lyrics_by_url, пишет в файл и возвращает текст
        """
        lyrics_from_txt = self.get_lyrics_from_txt(artist, track)
        if lyrics_from_txt:
            print(f'{artist} -- {track} -- from get_lyrics_from_txt method')
            return lyrics_from_txt
        else:
            lyrics_by_url = self.get_lyrics_by_url(artist, track)
            print(f'{artist} -- {track} -- from get_lyrics_from_url method')
            self.write_lyrics_to_txt(lyrics_by_url)
            return self.get_lyrics_from_txt(artist, track)


if __name__ == '__main__':
    TOKEN = os.getenv('GENIUS_COM_API_KEY')
    finder = LyricsFinder(TOKEN)
    finder.get_lyrics('nirvana', 'lithium')
