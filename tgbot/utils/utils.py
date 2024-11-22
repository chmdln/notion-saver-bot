import re 
import httpx
from bs4 import BeautifulSoup




def extract_urls(text):
    url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    urls = re.findall(url_pattern, text)
    return urls


def get_output_for_user(title, url, category, priority, timestamp):
    text = (
            f"Title: <b>{title}</b>\n"
            f"URL: {url}\n"
            f"Category: {category}\n"
            f"Priority: {priority}\n"
            f"Timestamp: {timestamp}\n"
        ) 
    return text 


def get_url_to_html(urls):
    text = ""
    for i, url in enumerate(urls):
        text += f"{i+1}. {url}\n"
    return text



async def get_page_title(url):
    async with httpx.AsyncClient(follow_redirects=True) as client:  
        try:
            response = await client.get(url, timeout=20)
            response.raise_for_status()  
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "No title found"
            return title.strip()

        except httpx.RequestError as e:
            return f"Request error: {e}"
        except Exception as e:
            return f"Error fetching the page: {e}"


def get_time(message):
    timestamp = message.date
    iso_8601_date = timestamp.isoformat() 
    if timestamp.tzinfo is None:
        iso_8601_date += "Z"

        
