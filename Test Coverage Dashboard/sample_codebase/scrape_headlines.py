import requests
import time
from bs4 import BeautifulSoup


def scrape_bbc(url):
    # Make an HTTP request to the BBC news Website
    response = requests.get(url)

    # Parse the HTML document
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract and return the news headlines
    headlines = soup.find_all("h2")
    return headlines


def save_headlines(headlines, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        for i, headline in enumerate(headlines, start=1):
            text = headline.get_text(strip=True)
            numbered_text = f"{i}. {text}"
            print(numbered_text, "\n")
            file.write(numbered_text + "\n")
            time.sleep(0.25)


if __name__ == "__main__":
    url = "https://www.bbc.com/news"
    output_file = "Task 3 - June 26/headlines.txt"
    headlines = scrape_bbc(url)
    save_headlines(headlines, output_file)
