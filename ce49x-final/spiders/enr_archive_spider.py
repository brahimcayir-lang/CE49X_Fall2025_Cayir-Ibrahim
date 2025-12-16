import scrapy


class ENRArchiveSpider(scrapy.Spider):
    name = "enr_archive"
    start_urls = ["https://www.enr.com/articles?page=0"]

    custom_settings = {"FEEDS": {"data/raw/enr_archive.json": {"format": "json", "overwrite": True}}}

    def parse(self, response):
        for article in response.css("h2 a::attr(href)").getall():
            yield response.follow(article, self.parse_article)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        title = response.css("h1::text").get(default="").strip()
        paras = response.css("div.body-copy p::text, article p::text").getall()
        full_text = " ".join([p.strip() for p in paras])
        date = response.css("time::attr(datetime)").get(default="")
        yield {
            "title": title,
            "date": date,
            "source": "ENR",
            "url": response.url,
            "full_text": full_text,
            "source_type": "scrapy",
            "raw_source": "ENRArchive",
        }





