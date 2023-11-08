import os
import json
import time
import requests
import bs4
import fake_headers


class Writer:
    def __init__(self, dir=os.getcwd(), json_name='result.json'):
        self.dir = dir
        self.json_name = json_name

    def write_json(self, dict):
        with open(f'{self.dir}/{self.json_name}', 'w', encoding='utf-8') as f:
            json.dump(dict, f, indent=4, sort_keys=True, ensure_ascii=False)


class Scraper:
    def __init__(self, url, words_search, region):
        self.url = url
        self.words_search = words_search
        self.region = region

    def scrape(self):
        pages = 0
        result = []

        while True:
            headers = fake_headers.Headers(browser="chrome", os="win")
            headers_dict = headers.generate()
            params = {
                'text': self.words_search,
                'area': self.region,
                'order_by': 'publication_time',
                'search_period': 0,
                'page': pages
            }
            response = requests.get(self.url, headers=headers_dict, params=params)
            main_html = bs4.BeautifulSoup(response.text, "lxml")

            main_articles = main_html.find("div", id="a11y-main-content")
            articles_tags = main_articles.find_all("div", class_="serp-item", limit=50)

            for article_tag in articles_tags:
                link = article_tag.find(class_="serp-item__title").get('href')
                company = article_tag.find('a', class_='bloko-link bloko-link_kind-tertiary').get_text().replace(' ', ' ')
                address = list(article_tag.find(class_="vacancy-serp-item__info").children)[1].text.replace(' ', ' ')
                if article_tag.find('span', class_='bloko-header-section-3'):
                    salary = article_tag.find('span', class_='bloko-header-section-3').get_text().replace(" ", '.')
                else:
                    salary = 'не указана'

                result.append({
                    'ссылка': link,
                    'вилка зп': salary,
                    'название компании': company,
                    'город': address
                })

            time.sleep(0.33)
            
            if len(articles_tags) < 20:
                break

            pages += 1

        return result


if __name__ == '__main__':
    scraper = Scraper('https://spb.hh.ru/search/vacancy', ' '.join(('Django', 'Flask',)), (1, 2,))
    writer = Writer()

    result = scraper.scrape()
    writer.write_json(result)

    print(len(result))
