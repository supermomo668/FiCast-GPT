import requests, time, tqdm
from bs4 import BeautifulSoup
from pathlib import Path
import urllib.request
from tqdm import tqdm
from urllib.parse import urlparse


DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
}

def get_prefetch_links(soup):
    prefetch_links = []
    download_tags_divs = soup.find_all('div', class_='download-tags-div')

    for div in download_tags_divs:
        a_tags = div.find_all('a', class_='download-button')
        for a_tag in a_tags:
            href = a_tag.get('href')
            # Ensure that the link contains an integer index after 'download-audio/'
            if href and 'download-audio/' in href:
                try:
                    index = int(href.split('download-audio/')[1].split('/')[0])
                    prefetch_links.append(href)
                except ValueError:
                    continue  # Skip if there's no valid integer index

    return prefetch_links


def extract_mp3_links(base_url, max_links, timeout=5):
    links_collected = 0
    page_number = 1
    mp3_links = []
    while links_collected < max_links:
        try:
            page_url = f"{base_url}/page/{page_number}/"
            response = requests.get(page_url, headers=DEFAULT_HEADERS, timeout=timeout)
            
            # Break if the page is empty or not found
            if response.status_code != 200 or not response.content:
                print(f"Page {page_url} returns: {response.status_code}")
                break

            soup = BeautifulSoup(response.content, 'html.parser')
            
            prefetch_links = get_prefetch_links(soup)
            if not prefetch_links:
                print(f"No prefetched links found on {page_url}")
                break  # Break if no prefetch links are found

            for download_page_link in tqdm(prefetch_links):
                tqdm.write(f"fetching links...{download_page_link}")
                download_page_response = requests.get(download_page_link, headers=DEFAULT_HEADERS, timeout=timeout)
                download_soup = BeautifulSoup(download_page_response.content, 'html.parser')
                button = download_soup.find('button', {'class': 'download'})
                
                if button and button['data-url'].endswith('.mp3'):
                    mp3_links.append(button['data-url'])
                    links_collected += 1
                    
                    if links_collected >= max_links:
                        return mp3_links
            page_number += 1
        except requests.RequestException as e:
            print(f"Error while requesting {page_url}: {e}")
            break  # Break the loop in case of a request exception
    return mp3_links


def download_links(
    mp3_links, download_folder='music'
    ):
    if not Path(download_folder).exists():
        Path(download_folder).mkdir()

    for url in tqdm(mp3_links):
        try:
            file_name = Path(urlparse(url).path).name
            download_path = Path(download_folder)/file_name
            req = urllib.request.Request(url, headers=DEFAULT_HEADERS)
            with urllib.request.urlopen(req) as response, open(download_path, 'wb') as out_file:
                data = response.read()
                out_file.write(data)
            tqdm.write(f"downloading links...{url}")
            time.sleep(0.1)  # Sleep for 0.1 second
        except Exception as e:
            print(f"Error downloading {url}: {e}")

if __name__ == '__main__':
    # Usage
    base_url = "https://www.chosic.com/free-music/lofi"
    max_links = 10  # For example, to collect 10 links

    mp3_links = extract_mp3_links(base_url, max_links)
    print(f"Collected {len(mp3_links)} links")
    download_links(mp3_links)