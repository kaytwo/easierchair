#!/usr/bin/env python
# -*- coding: utf-8 -*-


import getpass
import json
import os
import re
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request, FormRequest
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector

username = raw_input("easychair username:")
password = getpass.getpass()

try:
  outputfile = open('papers.json','w')
except IOError:
  print "something went wrong opening papers.json to dump paper data structure"

assert username
assert password
assert outputfile

class EasyChairReviews(scrapy.Spider):
  name = 'easychair'
  start_urls = ['https://www.easychair.org/account/signin.cgi']

  def parse(self,response):
    print response
    return [FormRequest.from_response(response,
      formdata={'name':username,'password':password},
        callback=self.after_login)]

  def after_login(self, response):
    '''
    load the paper bidding page, hard coded because javascript
    '''
    return Request(url="https://www.easychair.org/conferences/selection.cgi?a=9559460",callback=self.parse_bidpage)

  def parse_bidpage(self,response):
    allowed_links = re.compile(r".*submission_info_show.*")
    le = LinkExtractor(allow=allowed_links)
    links = le.extract_links(response)
    for link in links:
      yield Request(url=link.url,callback=self.parse_paper_page)
    return 

  def parse_paper_page(self,response):
    results = response.xpath('//*[@id="ec:table1"]//tr')
    thispaper = {}
    for row in results:
      subdoc = row.extract()
      xp = Selector(text=subdoc)
      elements = xp.xpath('//td//text()').extract()
      if elements[0].find('Paper') == 0:
        thispaper['number'] = elements[0]
      elif elements[0].find('Title') == 0:
        thispaper['title'] = ' '.join(elements[1:])
      # "author keywords"
      elif elements[0].find('Author') == 0:
        thispaper['keywords'] = elements[2:]
      elif elements[0].find('Abstract') == 0:
        thispaper['abstract'] = ' '.join(elements[1:])
    outputfile.write(json.dumps(thispaper) + '\n')
    # hurr i don't know how to call a cleanup fn in scrapy
    outputfile.flush()
    os.fsync(outputfile)

process = CrawlerProcess()

process.crawl(EasyChairReviews)
process.start()
