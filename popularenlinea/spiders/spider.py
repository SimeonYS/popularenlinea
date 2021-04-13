import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import PpopularenlineaItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'
base = 'https://www.popularenlinea.com/Personas/sala-de-prensa?PageNo={}'
class PpopularenlineaSpider(scrapy.Spider):
	name = 'popularenlinea'
	page = 1
	start_urls = [base.format(page)]

	def parse(self, response):
		post_links = response.xpath('//div[@class="blog-title"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		if len(post_links) == 10:
			self.page += 1
			yield response.follow(base.format(self.page), self.parse)

	def parse_post(self, response):
		date = response.xpath('//div[@class="col-sm-10 list-section newsroom-list-section"]/span/text()').get().split(':')[1].strip()
		title = response.xpath('//div[@data-name="Page Field: Title"]/text()').get().strip()
		content = response.xpath('//div[@class="newsroom article-content"]//text()[not (ancestor::div[@class="ms-rtestate-read ms-rte-wpbox"] or ancestor::div[@id="ctl00_PlaceHolderMain_ctl04_ctl00_label"])] | //div[@class="ms-rtestate-notify  ms-rtestate-read a2a32f2f-1071-497b-8044-698379a05699"]/p//text() |//div[@class="ms-rtestate-read ms-rte-wpbox"]//p/text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=PpopularenlineaItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
