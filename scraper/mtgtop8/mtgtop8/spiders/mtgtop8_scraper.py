import scrapy
from scrapy.utils.response import open_in_browser

import pandas as pd
import re

class MtgTop8Spider(scrapy.Spider):
    name = "mtgtop8"
    start_urls = [
        "https://mtgtop8.com/format?f=EDH",
    ]
  
    def parse(self, response):
        for s14 in response.css("div.hover_tr div.S14 a"):
            text = s14.css('a::text').get()
            link = s14.css('a::attr(href)').get()
            yield {
                'text': text,
                'link': link,
            }
class MtgTop8SearchSpider(scrapy.Spider):
    name = "mtgtop8Search"
    start_urls = [
        "https://mtgtop8.com/search",
    ]
  
    def parse(self, response):
        for s14 in response.css("#arch_EDH option"):
            text = s14.css('option::text').get()
            value = s14.xpath('@value').get()
            yield {
                'text': text.casefold(),
                'value': value,
            }
            
class MtgTop8SearchWithParamSpider(scrapy.Spider):
    name = "mtgtop8SearchParams"
    
    def __init__(self, *args, **kwargs): 
        super(MtgTop8SearchWithParamSpider, self).__init__(*args, **kwargs) 
        
        FILE_PATH = "scraps/mtgtop8_commanders.json"
        datas = pd.read_json(FILE_PATH)
        self.commander_name = kwargs.get('commander_name').casefold() 
        
        self.date_start = "21/05/2022"
        if kwargs.__contains__('date_start'):
            self.date_start = kwargs['date_start']
            
        self.logger.info("scraping for : " + self.commander_name + 'from : ' + self.date_start)
        self.commander_id = datas.loc[datas['text']==self.commander_name].values[0][1]     
        
    def start_requests(self):
        deck_id = self.commander_id
        date_start_str = self.date_start
        self.logger.info(deck_id)
        self.logger.info(date_start_str)
        return [scrapy.FormRequest("https://mtgtop8.com/search",
                                   formdata={'current_page': '', 
                                             'event_titre': '',
                                             'deck_titre': '',
                                             'player': '',
                                             'format': '',
                                             'archetype_sel[VI]': '',
                                             'archetype_sel[LE]': '',
                                             'archetype_sel[MO]': '',
                                             'archetype_sel[PI]': '',
                                             'archetype_sel[EX]': '',
                                             'archetype_sel[HI]': '',
                                             'archetype_sel[ST]': '',
                                             'archetype_sel[BL]': '',
                                             'archetype_sel[PAU]': '',
                                             'archetype_sel[EDH]': deck_id,
                                             'archetype_sel[HIGH]': '',
                                             'archetype_sel[EDHP]': '',
                                             'archetype_sel[CHL]': '',
                                             'archetype_sel[PEA]': '',
                                             'archetype_sel[EDHM]': '',
                                             'archetype_sel[ALCH]': '',
                                             'archetype_sel[cEDH]': '',
                                             'archetype_sel[EXP]': '',
                                             'compet_check[P]':'1',
                                             'compet_check[M]': '1',
                                             'compet_check[C]': '1',
                                             'compet_check[R]': '1',
                                             'MD_check': '1',
                                             'cards': '',
                                             'date_start': date_start_str,
                                             'date_end': '',},
                                   cookies=[{'name': 'cookieSeen',
                                        'value': 'shown',
                                        'domain': 'mtgtop8.com',
                                        'path': '/'}],
                                   callback=self.parse)]
    def parse(self, response):
        open_in_browser(response)
        for decks in response.css(".S12 a"):
            text = decks.css('a::text').get()
            link = decks.css('a::attr(href)').get()
            yield {
                'text': text,
                'link': link,
            }
            
class MtgTop8SpiderDeck(scrapy.Spider):
    name = "mtgtop8Deck"
    start_urls = []
  
    def __init__(self, *args, **kwargs): 
        super(MtgTop8SpiderDeck, self).__init__(*args, **kwargs) 
        
        commander_name = kwargs.get('commander_name') 
        commander_file = re.sub("[ ,/]", "_", commander_name)
        self.FILE_PATH = 'scraps/'+ commander_file +'_links.json'
        
        datas = pd.read_json(self.FILE_PATH)
        
        for row in datas.itertuples():
            self.start_urls.append("https://mtgtop8.com/" + row.link)
        self.logger.info("scraping for : " + " --- ".join(self.start_urls))
        
        
        
    def parse(self, response):
        for s14 in response.css(".deck_line"):
            
            count = s14.css('div::text').get()
            card = s14.css('.L14::text').get()
            yield {
                'count': count,
                'card': card,
                'url': response.url
            }