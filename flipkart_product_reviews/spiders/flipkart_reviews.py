import scrapy
from urllib.parse import urljoin


class FlipkartReviewsSpider(scrapy.Spider):
    name = "flipkart_reviews"

    def start_requests(self):
        itm_list = ['3485a56f6e676']
        for fkid in itm_list:
            flipkart_reviews_url = f'https://www.flipkart.com/product-reviews/product-reviews/itm{fkid}'
            yield scrapy.Request(url=flipkart_reviews_url, callback=self.parse_reviews, meta={'fkid': fkid, 'retry_count': 0})

    def parse_reviews(self, response):
        fkid = response.meta['fkid']
        retry_count = response.meta['retry_count']


        ## Get Next Page Url
        next_page_relative_url = response.css(".yFHi8N a:last-child::attr(href)").get()
        if next_page_relative_url is not None:
            retry_count = 0
            next_page = urljoin('https://www.flipkart.com/', next_page_relative_url)
            yield scrapy.Request(url=next_page, callback=self.parse_reviews, meta={'fkid': fkid, 'retry_count': retry_count})

        elif retry_count < 3:
            retry_count = retry_count+1
            yield scrapy.Request(url=response.url, callback=self.parse_reviews, dont_filter=True, meta={'fkid': fkid, 'retry_count': retry_count})

        
        
        ## Parse Product Reviews
        review_elements = response.css("._1YokD2>div._1AtVbE:nth-child(n+3):not(:last-child)")
        for review_element in review_elements:
            yield {
                    "fkid": fkid,
                    "customer name": review_element.css("._2sc7ZR::text").get().title(),
                    "title": review_element.css("*._2-N8zT::text").get(),
                    "text": "".join(review_element.css("div.t-ZTKy>div :not(span) ::text").getall()).strip(),
                    "location": review_element.css("*._2mcZGG span:nth-child(2) ::text").get().lstrip(', '),
                    "date": review_element.css("p[class=_2sc7ZR] ::text").get(),
                    "verified": bool(review_element.css("p[class=_2mcZGG] ::text").get()),
                    "rating": review_element.css("*[class*=_3LWZlK] ::text").get(),
                    }
