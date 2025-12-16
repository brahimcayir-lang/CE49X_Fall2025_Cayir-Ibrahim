import scrapy


class ConstructionDiveSpider(scrapy.Spider):
    name = "constructiondive_archive"
    start_urls = ["https://www.constructiondive.com/archives/"]

    custom_settings = {"FEEDS": {"data/raw/constructiondive_archive.json": {"format": "json", "overwrite": True}}}

    def parse(self, response):
        for article in response.css("h3 a::attr(href)").getall():
            yield response.follow(article, self.parse_article)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        title = response.css("h1::text").get(default="").strip()
        paras = response.css("article p::text").getall()
        full_text = " ".join([p.strip() for p in paras])
        date = response.css("time::attr(datetime)").get(default="")
        yield {
            "title": title,
            "date": date,
            "source": "ConstructionDive",
            "url": response.url,
            "full_text": full_text,
            "source_type": "scrapy",
            "raw_source": "ConstructionDiveArchive",
        }





