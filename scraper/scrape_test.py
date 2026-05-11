import requests
from bs4 import BeautifulSoup
import json

url = "https://www.bbc.com/news"

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

titles = soup.find_all("h2")

articles = []

for t in titles[:10]:
    title_text = t.text.strip()
    
    if title_text:
        articles.append({
            "title": title_text,
            "source": "BBC News"
        })

# SAVE TO FILE (BRONZE LAYER)
with open("data/bronze/articles.json", "w", encoding="utf-8") as f:
    json.dump(articles, f, indent=4, ensure_ascii=False)

print("Saved successfully!")