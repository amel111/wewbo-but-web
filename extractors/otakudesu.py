from .base import BaseExtractor
from bs4 import BeautifulSoup
import base64
import json
import requests

class OtakudesuExtractor(BaseExtractor):
    name = "otakudesu"
    host = "https://otakudesu.best"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
        "Referer": "https://otakudesu.best"
    }

    def __init__(self):
        super().__init__()
        self.session.headers.update(self.headers)

    def search(self, query):
        url = f"{self.host}/?s={query}&post_type=anime"
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for link in soup.select("h2 a"):
                results.append({
                    "title": link.get_text(strip=True),
                    "url": link.get('href')
                })
            return results
        except Exception as e:
            print(f"Error searching: {e}")
            return []

    def get_episodes(self, anime_url):
        try:
            response = self.session.get(anime_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            episodes = []
            lists = soup.select("div.episodelist ul")
            if len(lists) > 1:
                episode_list = lists[1]
            elif len(lists) == 1:
                episode_list = lists[0]
            else:
                return []

            li_items = episode_list.select("li")
            for li in li_items:
                a_tag = li.find('a')
                if a_tag:
                    episodes.append({
                        "title": a_tag.get_text(strip=True),
                        "url": a_tag.get('href')
                    })
            return episodes
        except Exception as e:
            print(f"Error getting episodes: {e}")
            return []

    def _get_nonce(self):
        url = f"{self.host}/wp-admin/admin-ajax.php"
        data = {"action": "aa1208d27f29ca340c92c66d1926f13f"}
        try:
            res = self.session.post(url, data=data)
            data_json = res.json()
            return data_json.get("data")
        except Exception as e:
            print(f"Error getting nonce: {e}")
            return None

    def get_stream_url(self, episode_url):
        try:
            response = self.session.get(episode_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            nonce = self._get_nonce()
            if not nonce:
                return {"error": "Failed to get nonce"}
                
            mirrors = soup.select("div.mirrorstream ul li")
            target_mirror = None
            target_source_name = ""
            
            for li in mirrors:
                source_text = li.get_text(strip=True).lower()
                if "pdrain" in source_text or "desudesu" in source_text:
                    target_mirror = li
                    target_source_name = source_text
                    break
            
            if not target_mirror and mirrors:
                target_mirror = mirrors[0]
                target_source_name = target_mirror.get_text(strip=True)

            if not target_mirror:
                return {"error": "No mirrors found"}

            a_tag = target_mirror.find('a')
            if not a_tag:
                return {"error": "No link in mirror"}
                
            data_content = a_tag.get('data-content')
            decoded_json = json.loads(base64.b64decode(data_content).decode('utf-8'))

            decoded_json["nonce"] = nonce
            decoded_json["action"] = "2a3505c93b0035d3f455df82bf976b84"
            
            post_url = f"{self.host}/wp-admin/admin-ajax.php"
            res = self.session.post(post_url, data=decoded_json)
            res_json = res.json()
            
            data_embed = res_json.get("data")
            if not data_embed:
                 return {"error": "No embed data returned"}
                 
            iframe_html = base64.b64decode(data_embed).decode('utf-8')
            iframe_soup = BeautifulSoup(iframe_html, 'html.parser')
            iframe = iframe_soup.find('iframe')
            if not iframe:
                 return {"error": "No iframe found in response"}
                 
            iframe_src = iframe.get('src')
            
            if "pdrain" in target_source_name.lower():
                 return {"type": "iframe", "url": iframe_src}
                 
            try:
                vid_res = self.session.get(iframe_src, headers={"Referer": episode_url})
                vid_soup = BeautifulSoup(vid_res.text, 'html.parser')
                source = vid_soup.find('source')
                if source:
                    return {"type": "mp4", "url": source.get('src')}
            except:
                pass
                
            return {"type": "iframe", "url": iframe_src}

        except Exception as e:
            return {"error": str(e)}
