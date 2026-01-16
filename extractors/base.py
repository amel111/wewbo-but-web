from abc import ABC, abstractmethod
import requests

class BaseExtractor(ABC):
    def __init__(self):
        self.session = requests.Session()

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def host(self):
        pass

    @abstractmethod
    def search(self, query):
        pass

    @abstractmethod
    def get_episodes(self, anime_url):
        pass

    @abstractmethod
    def get_stream_url(self, episode_url):
        pass
