from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instaparser.spiders.instagram import InstagramSpider
from instaparser import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)

    # search = input("Введите список пользователей Instagram через пробел: ").split()
    search = ["elena_30287",
              "digital_goose",
              "koro4e.etosamoe",
              "shop.nasiliutochkanet",
              ]
    process.crawl(InstagramSpider, search=search)

    process.start()
