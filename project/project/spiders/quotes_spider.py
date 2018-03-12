import scrapy
import re

def to_write(uni_str):
    return urllib.unquote(uni_str.encode('utf8')).decode('utf8')



class QuotesSpider(scrapy.Spider):
    name = "dsl"
    allowed_domains = ["dsl.sk"]


    def start_requests(self):
        urls = [
            'http://www.dsl.sk',
            'http://www.dsl.sk/index_news.php?page=20861'
        ]

        custom_settings = {
            'DEPTH_LIMIT': '50',
        }
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        next_pages = response.css('a::attr(href)')
        for next_page in next_pages.extract():
            result = re.search(".*article\.php\?article=\d+", next_page)
            if result:
                yield response.follow(result[0], self.parse_article)
            elif next_page:
                yield response.follow(next_page, self.parse)


    def parse_article(self, response):
        title = response.css('#body font.page_title::text').extract_first()
        article_perex = response.css('#body b font.article_perex::text').extract_first()
        tags = response.css('#body span.tag_empty span a::text').extract()
        date = response.css('#body td font.article_perex::text').extract_first()
        date = re.search("(?<=, )(.+)", date)[0]
        article_parts = response.css('#body font.article_body::text').extract()

        full_article = ""
        for art in article_parts:
            art = re.sub('\\r|\\n', '', art)
            full_article = full_article + art

        yield {
            'title': title,
            'article_perex': article_perex,
            'tags':tags,
            'date':date,
            'artical':full_article
        }
