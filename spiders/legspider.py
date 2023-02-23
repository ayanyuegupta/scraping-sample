# -*- coding: utf-8 -*-
import scrapy
import os
import pickle
import re
import subprocess

from scrapy.http import Request
from scrapy.http import FormRequest
from scrapy.exceptions import CloseSpider

class legspider(scrapy.Spider):

    name = 'legspider'

    def __init__(self, path, year, genre, *args, **kwargs):

        super(legspider, self).__init__(*args, **kwargs)

        self.path = path
        self.year = year
        self.genre = genre
        self.d = {}


    def start_requests(self):
        
        year = 2000
        url = 'https://www.legislation.gov.uk/{}/{}?&page=1'.format(self.genre, self.year)

        yield scrapy.Request(url, callback=self.parse)

    
    def parse(self, response):

        urls = [response.urljoin(item) for item in \
                response.xpath('//*[@id="content"]/table/tbody//tr/td[1]/a/@href').extract()]

        for url in urls:

            yield scrapy.Request(url, callback=self.parse_page)

        if 'page=' in response.url:

            next_page = int(response.url.split('=')[-1]) + 1
            next_url = 'https://www.legislation.gov.uk/{}/{}?&page={}'.format(self.genre, self.year, next_page)

        else:
            next_url = 'https://www.legislation.gov.uk/{}/{}&page=2'.format(self.genre, self.year)

        yield scrapy.Request(next_url, callback=self.parse)

    
    def parse_page(self, response):
        
        pdf_link = '//*[@id="printOptions"]/ul/li[2]/ul/li[1]/a/@href' 
        if response.xpath(pdf_link).extract() != []:
            doc_url = response.xpath(pdf_link).extract()[0]
        else:
            pdf_link = '//*[@id="viewLegSnippet"]/p/a/@href'
            doc_url = response.xpath(pdf_link).extract()[0]

        title = response.xpath('//*[@id="pageTitle"]/text()').extract()[0]
        title = '_'.join(title.split()).lower() + '.pdf'
        self.d[response.urljoin(doc_url)] = title

        yield scrapy.Request(response.urljoin(doc_url), callback=self.get_doc)


    def get_doc(self, response):
                
        title = self.d[response.url]
        
        with open('d.pickle', 'rb') as f:
            d = pickle.load(f)
        
        for key in d:
            if self.genre in d[key]:

                path = self.path + '/{}'.format(key)

        if not os.path.exists(path):
            os.makedirs(path)

        with open(path + '/' + title, 'wb') as f:
            f.write(response.body)
       
        dec_path = path + '/{}-leg-'.format(self.year) + title
        subprocess.call(['qpdf', '--decrypt', path + '/' + title, dec_path])
        os.remove(path + '/' + title) 
        subprocess.call(['pdftotext', dec_path])
        os.remove(dec_path)



        
        



