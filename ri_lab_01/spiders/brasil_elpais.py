# -*- coding: utf-8 -*-
import scrapy
import json
from datetime import datetime

from ri_lab_01.items import RiLab01Item
from ri_lab_01.items import RiLab01CommentItem


class BrasilElpaisSpider(scrapy.Spider):
    name = 'brasil_elpais'
    allowed_domains = ['brasil.elpais.com']
    start_urls = []

    def __init__(self, *a, **kw):
        super(BrasilElpaisSpider, self).__init__(*a, **kw)
        with open('seeds/brasil_elpais.json') as json_file:
                data = json.load(json_file)
        self.start_urls = list(data.values())

    def parse(self, response):

        for href in response.css("h2.articulo-titulo a::attr(href)"):
            yield response.follow(href, self.parse_content, meta={'url': response.url})

        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

    def parse_content(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()

        #Necessidade de ajustes no formato da data
        formatedDate = extract_with_css('time::attr(datetime)')
        #seleciona parte da data importante capturada pelo crawler
        formatedDate = formatedDate[:-6]
        #formata da maneira requisitada
        formatedDate = datetime.strptime(formatedDate, '%Y-%m-%dT%H:%M:%S')

        #Recuperar o texto (dirty mode)
        #for content in response.css('div.contenedor'): 
        #    recoveredText = content.css('div.articulo__contenedor p::text').getall()
        #    recoveredText = "".join(recoveredText)

        #Recuperar o texto por meio de xpath
        recoveredText = response.xpath('//div[contains(@class, "articulo__contenedor")]//p/text() | \
                                //div[contains(@class, "articulo__contenedor")]//p/span/text()').getall()
        recoveredText = "".join(recoveredText)

        yield {
            'title': extract_with_css('h1.articulo-titulo::text'),
            'sub-title': extract_with_css('h2.articulo-subtitulo::text'),
            'author': extract_with_css('span.autor-nombre  a::text'),
            'date': formatedDate,
            'url': response.url,
            'section': response.meta['url'].split('/')[-2],
            'text':recoveredText
            #'text': extract_with_css('div.articulo-cuerpo p::text')
        }
        
