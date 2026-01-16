from extractors import ExtractorFactory
import requests
from bs4 import BeautifulSoup
import json

def debug_hianime():
    extractor = ExtractorFactory.get_extractor("hianime")
    
    # search "one piece"
    print("Searching...")
    results = extractor.search("one piece")
    first_anime = results[0]
    print(f"Anime: {first_anime['title']}")
    
    # get episodes
    print("Getting episodes...")
    episodes = extractor.get_episodes(first_anime['url'])
    first_ep = episodes[0]
    print(f"Episode: {first_ep['title']} (URL: {first_ep['url']})")
    
    ep_id = first_ep['url'].split(":")[1]
    
    # get servers
    print(f"Getting servers for ID {ep_id}...")
    servers_url = f"{extractor.host}/ajax/v2/episode/servers?episodeId={ep_id}"
    res = extractor.session.get(servers_url)
    data = res.json()
    soup = BeautifulSoup(data.get("html"), 'html.parser')
    server_item = soup.select_one("div.server-item")
    mega_id = server_item.get("data-id")
    print(f"MegaID: {mega_id}")
    
    # get initial link
    print("Getting initial link...")
    url = f"{extractor.host}/ajax/v2/episode/sources?id={mega_id}"
    res = extractor.session.get(url)
    data = res.json()
    link = data.get("link")
    print(f"Link: {link}")
    
    # Fetch content of the link
    print("Fetching Link Content...")
    headers = {
        "User-Agent": extractor.headers["User-Agent"],
        "Referer": extractor.host,
        "Origin": extractor.host
    }
    res_mc = extractor.session.get(link, headers=headers)
    print(f"Status: {res_mc.status_code}")
    
    
    # Debug getSources logic
    print("Debugging getSources...")
    
    # 1. file_id
    soup = BeautifulSoup(res_mc.text, 'html.parser')
    fix_area = soup.select_one("div.fix-area")
    file_id = fix_area.get('data-id') if fix_area else None
    print(f"Extracted FileID: {file_id}")
    
    # 2. nonce
    import re
    nonce = None
    patterns = [
        r'<script nonce="([^"]+)"',
        r"window\._xy_ws\s*=\s*'([^']+)'",
        r'window\._xy_ws\s*=\s*"([^"]+)"',
        r"<!-- _is_th:\s*(.+?)\s*-->",
        r'<div[^>]+data-dpi="([^"]+)"'
    ]
    for p in patterns:
        m = re.search(p, res_mc.text)
        if m:
            nonce = m.group(1)
            print(f"Matched Nonce Pattern: {p}")
            break
            
    print(f"Extracted Nonce: {nonce}")
    
    if file_id and nonce:
        # Construct URL
        # domain = ...
        domain = link.split("/embed-2")[0]
        sources_url = f"{domain}/embed-2/ajax/e-1/getSources?id={file_id}&_k={nonce}"
        print(f"Sources URL: {sources_url}")
        
        headers_ajax = headers.copy()
        headers_ajax["Referer"] = link
        headers_ajax["X-Requested-With"] = "XMLHttpRequest" # Often needed
        
        res_sources = extractor.session.get(sources_url, headers=headers_ajax)
        print(f"Sources Status: {res_sources.status_code}")
        print(f"Sources Content: {res_sources.text[:500]}") # Print first 500 chars

if __name__ == "__main__":
    debug_hianime()
