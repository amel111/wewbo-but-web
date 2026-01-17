from .base import BaseExtractor
from bs4 import BeautifulSoup
import re

class OploversExtractor(BaseExtractor):
    name = "oploverz"
    host = "https://anime.oploverz.ac"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://anime.oploverz.ac"
    }

    def __init__(self):
        super().__init__()
        self.session.headers.update(self.headers)

    def _normalize_url(self, url):
        """Ensure URL is a full URL, not relative"""
        if url.startswith('http'):
            return url
        if url.startswith('/'):
            return f"{self.host}{url}"
        return f"{self.host}/{url}"

    def search(self, query):
        """Search for anime by query - scrapes series list and filters locally"""
        # The site uses JavaScript for search, so we scrape the series list and filter
        url = f"{self.host}/series"
        try:
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            all_anime = []
            seen_urls = set()
            query_lower = query.lower()
            
            # Find all series links
            for link in soup.select('a[href*="/series/"]'):
                href = link.get('href', '')
                
                # Skip episode links
                if '/episode/' in href:
                    continue
                
                # Skip duplicates
                if href in seen_urls:
                    continue
                seen_urls.add(href)
                
                # Get title from the link text
                title = link.get_text(strip=True)
                if not title or len(title) < 2:
                    continue
                
                # Skip generic button text
                if title in ['Mulai Sekarang', 'Tonton Sekarang', 'Sebelumnya', 'Selanjutnya', 
                            'Beranda', 'Daftar Anime', 'Oploverz', 'Jadwal Rilis', 'Hubungi Kami']:
                    continue
                
                # Skip if just numbers or metadata
                if title.replace(' ', '').replace('/', '').isdigit():
                    continue
                
                # Clean title (remove metadata prefix like "18/20131000")
                title = re.sub(r'^\d+/\d+\s*', '', title).strip()
                
                if title:
                    all_anime.append({
                        "title": title,
                        "url": href
                    })
            
            # Filter by query (case-insensitive)
            results = []
            for anime in all_anime:
                if query_lower in anime['title'].lower():
                    # Check for duplicate titles in results
                    if not any(r['url'] == anime['url'] for r in results):
                        results.append(anime)
            
            return results
        except Exception as e:
            print(f"Error searching: {e}")
            return []

    def get_episodes(self, anime_url):
        """Get episode list for an anime"""
        try:
            # Normalize URL to full path
            full_url = self._normalize_url(anime_url)
            response = self.session.get(full_url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            episodes = []
            seen_urls = set()
            
            # Find all episode links
            for link in soup.select('a[href*="/episode/"]'):
                href = link.get('href', '')
                
                if href in seen_urls:
                    continue
                seen_urls.add(href)
                
                # Extract episode number from URL
                match = re.search(r'/episode/(\d+)', href)
                if match:
                    ep_num = match.group(1)
                    title = f"Episode {ep_num}"
                else:
                    title = link.get_text(strip=True) or "Episode"
                
                episodes.append({
                    "title": title,
                    "url": href
                })
            
            # Sort by episode number
            def get_ep_num(ep):
                match = re.search(r'/episode/(\d+)', ep['url'])
                return int(match.group(1)) if match else 0
            
            episodes.sort(key=get_ep_num)
            
            return episodes
        except Exception as e:
            print(f"Error getting episodes: {e}")
            return []

    def get_stream_url(self, episode_url):
        """Get stream URL for an episode"""
        try:
            # Normalize URL to full path
            full_url = self._normalize_url(episode_url)
            response = self.session.get(full_url, timeout=15)
            # Find the Blogger URL in the hidden JSON data
            # Pattern: url:"(https://www.blogger.com/video.g?token=[^"]+)"
            blogger_match = re.search(r'url:"(https://www\.blogger\.com/video\.g\?token=[^"]+)"', response.text)
            
            if blogger_match:
                return {
                    "type": "iframe",
                    "url": blogger_match.group(1),
                    # We still need navigation links
                    "prev_ep": self._extract_nav_link(response.text, ['sebelum', 'prev'], episode_url),
                    "next_ep": self._extract_nav_link(response.text, ['selanjut', 'next'], episode_url)
                }

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # The site uses JavaScript to load the video player
            # We embed the episode page itself in an iframe as fallback
            stream_data = {
                "type": "iframe",
                "url": full_url
            }
            
            # Extract Navigation (Next/Prev) - look for navigation links with specific text
            for link in soup.select('a'):
                text = link.get_text(strip=True).lower()
                href = link.get('href', '')
                
                if not href or '/episode/' not in href:
                    continue
                
                if 'sebelum' in text or 'prev' in text:
                    stream_data["prev_ep"] = href
                elif 'selanjut' in text or 'next' in text:
                    stream_data["next_ep"] = href
            
            return stream_data

        except Exception as e:
            return {"error": str(e)}

    def _extract_nav_link(self, html, keywords, current_url):
        """Helper to extract navigation links from HTML text directly"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            for link in soup.select('a'):
                text = link.get_text(strip=True).lower()
                href = link.get('href', '')
                if not href or '/episode/' not in href:
                    continue
                if any(k in text for k in keywords):
                    return href
        except:
            pass
        return None

