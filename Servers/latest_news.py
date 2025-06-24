import requests
from bs4 import BeautifulSoup

def fetch_latest_news():
    uni_news_url = 'https://su.edu.eg/index.php/homepage_read_all_news/'
    
    # request
    req = requests.get(uni_news_url)

    if req.status_code != 200:
        print('errrrrrrrrrrrrrrrrrrror')
    
    # extract news articles
    soup = BeautifulSoup(req.text, 'html.parser')

    news_articles = []
    for article in soup.find_all('h3', class_='gdlr-core-blog-title gdlr-core-skin-title'):
        request_url = article.find('a')['href']
        new_req = requests.get(request_url)
        soup_article = BeautifulSoup(new_req.text, 'html.parser')
        new = {
            'url': article.find('a')['href'],
            'title': article.find('a').get_text(strip=True),
            'content': soup_article.find_all('p')
        }

        news_articles.append(new)

    return news_articles



print(fetch_latest_news())

    