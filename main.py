import requests
from pprint import pprint
from bs4 import BeautifulSoup
import os

BASE_URL = 'https://api.genius.com/'


class LyricsFinder:
    def __init__(self, token):
        self.genius_oauth = token
        self.lyrics_dir = os.path.join(os.getcwd(), 'lyrics' + os.sep)

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
            if artist.lower().strip() in artist_name.lower():
                return lyrics_url

    def get_lyrics_by_url(self, artist, track):
        """
        метод парсит страницу, полученную с помощью get_lyrics_url
        возвращает текст песни
        """
        result = {}
        url = self.get_lyrics_url(artist, track)
        if not url:
            raise Exception('failed to get url on request')
        post_page = requests.get(url)
        soup = BeautifulSoup(post_page.text, 'html.parser')
        text = soup.select('[class~=lyrics]')
        lyrics = text[0].text
        result.update({'artist': artist, 'track': track, 'lyrics': lyrics})
        return result

    def write_lyrics_to_txt(self, lyrics):
        artist = lyrics['artist'].capitalize()
        track = lyrics['track'].capitalize()
        title = f'{artist} -- {track}'
        with open(f'{self.lyrics_dir}{title}.txt', 'w', encoding='utf=8') as f:
            f.write(title)
            for line in lyrics['lyrics']:
                f.write(line)

    def get_lyrics_from_txt(self, artist, track):
        file_name = f'{artist.capitalize()} -- {track.capitalize()}.txt'
        dir_content = os.listdir(self.lyrics_dir)
        if file_name in dir_content:
            with open(f'{self.lyrics_dir}{file_name}', 'r', encoding='utf-8') as f:
                lyrics = f.read()
            return lyrics
        else:
            return None

    def get_lyrics(self, artist, track):
        lyrics_from_txt = self.get_lyrics_from_txt(artist, track)
        if lyrics_from_txt:
            print('from get_lyrics_from_txt method')
            return lyrics_from_txt
        else:
            lyrics_by_url = self.get_lyrics_by_url(artist, track)
            print('from get_lyrics_by_url method')
            self.write_lyrics_to_txt(lyrics_by_url)
            return self.get_lyrics_from_txt(artist, track)


if __name__ == '__main__':
    TOKEN = ''
    finder = LyricsFinder(TOKEN)

    print(finder.get_lyrics('nirvana', 'come as you are'))
