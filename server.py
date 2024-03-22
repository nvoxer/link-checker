from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup
import requests
from pytz import utc
import time
from datetime import datetime

# base URL 
base_url = "https://foros.3dgames.com.ar/threads/942062-ofertas-online-argentina/"

# File to store encountered links
links_file = "encountered_links.txt"

# Function to retrieve links from the last page of the thread
def get_links_from_last_page():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    global links_file
    last_page_url = get_last_page_url()
    if last_page_url:
        print(f"Extracting links from the last page: {last_page_url}")
        page = requests.get(last_page_url, headers=headers)
        if page.status_code == 200:
            soup = BeautifulSoup(page.text, 'html.parser')
            new_links = set()
            for post_details in soup.find_all(class_="postcontent restore"):
                links = post_details.find_all('a', href=True)
                for link in links:
                    if not (link['href'].startswith("showthread.php?p=") or link['href'].startswith("showthread.php?s=") or link['href'].startswith("https://foros.3dgames.com.ar") or link['href'].startswith("mailto:")):
                        href = link['href']
                        new_links.add(href)
                        if not link_exists(href, links_file):
                            save_link(href, links_file)
                            print(href)
            # Check if there are new links
            if not new_links.difference(load_links(links_file)):
                print("No new links found")
        else:
            print(f"Failed to retrieve last page: {last_page_url}")
          
# extract <h1> OR <title> from encountered link       
def fetch_h1_text(url):
    h1_text = "Título no encontrado"  # Default value if no title or h1 is found
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, timeout=25, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            h1_tag = soup.find('h1')
            if h1_tag and h1_tag.text.strip():
                h1_text = h1_tag.text.strip()
            else:
                title_tag = soup.find('title')
                if title_tag and title_tag.text.strip():
                    h1_text = title_tag.text.strip()
    except requests.RequestException:
        h1_text = "Título no encontrado | Timeout"
    return h1_text


# Function to retrieve the URL of the last page
def get_last_page_url():
    page = requests.get(base_url)
    if page.status_code == 200:
        soup = BeautifulSoup(page.content, 'html.parser')
        last_page_span = soup.find("span", class_="first_last")
        if last_page_span:
            last_page_link = last_page_span.find("a")
            if last_page_link:
                last_page_url = last_page_link.get("href")
                # Check if the URL is relative, and if so, add the base URL
                if not last_page_url.startswith('http'):
                    last_page_url = base_url + last_page_url
                return last_page_url
            else:
                print("Last page link not found")
        else:
            print("Pagination not found")
    else:
        print(f"Failed to retrieve thread: {base_url}")

# Function to check if a link exists in the file
def link_exists(link, filename):
    with open(filename, 'r') as file:
        return link in file.read()

# Function to load links from the file
def load_links(filename):
    with open(filename, 'r') as file:
        return set(file.read().splitlines())
        

# Function to save a link to the file
def save_link(link, filename):
    current_time = datetime.now() # + timedelta(hours=2)  # para ajustar timezone
    current_time_str = current_time.strftime("%A %e, %B  %H:%M")
    h1_text = fetch_h1_text(link)
    with open(filename, 'a') as file:
        file.write(f"{current_time_str} — {h1_text} > {link}\n")

# scheduler
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(get_links_from_last_page, 'interval', seconds=60, timezone=utc)
scheduler.start()


# web server

app = Flask(__name__)

# File containing encountered links
links_file = "encountered_links.txt"

# Function to read links from the file
def read_links_from_file():
    with open(links_file, 'r') as file:
        links = file.readlines()
    return [line.strip() for line in links]

@app.route('/')
def index():
    links = read_links_from_file()
    links_with_datetime = [link.split(' > ') for link in links]
    return render_template('index.html', links=links_with_datetime)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=False)
