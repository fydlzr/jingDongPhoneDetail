# -*- coding:utf-8 -*-
import os
import os.path
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import scrapy
from bs4 import BeautifulSoup as bs
from scrapy.http import Request
from scrapy.spider import BaseSpider
from crawler.items import CrawlerItem
from selenium import selenium
import re, urllib,urllib2,json

totalPages = 31
beginWith = 1

crawled = set()
pairCount = {}

def has_refer(tag):
	return tag.has_attr('class') and 'refer' in tag['class']

def getFirstString(tag):
	for s in tag.stripped_strings:
		return s

def getListSingle(tag):
	l = []
	for s in tag.stripped_strings:
		if s!="":l.append(s)
	return l
def getListString(tag):
	l = ''
	for s in tag.stripped_strings:
		l += s
	return l
def getList(tags):
	l = []

	for tag in tags:
		flag = False
		v = ''
		for s in tag.stripped_strings:
			if s=='':continue
			if flag==False:
				l.append(s)
				flag = True
			else:
				v += s+'  '
		l.append(v)
	return l

def post(url, parameter):
	data = urllib.urlencode(parameter)
	req = urllib2.Request(url, data)
	response = urllib2.urlopen(req)
	return response.read()

def get(url, parameter):
	data = urllib.urlencode(parameter)
	req = urllib2.Request(url+'?' +data)
	response = urllib2.urlopen(req)
	return response.read()

class JDspSpider(scrapy.Spider):
	name = "JD_QAsp"
	allowed_domains = ['jd.com', 'jd.hk']

	for parent,dirnames,filenames in os.walk(r'F:\git\jdcrawler\out\ed'): 
		for filename in filenames:
			crawled.add(filename.strip())
	

	start_urls = (
		# 'http://club.jd.com/consultation/3046726-62273213.html',
		'http://item.jd.hk/1957483655.html',
		# 'http://club.jd.com/allconsultations/3046726-1-1.html',
		# 'http://item.jd.hk/10345569383.html',
		# 'http://item.jd.com/10228033653.html',
		# 'http://list.jd.com/list.html?cat=9987,653,655&page=1&go=0&JL=6_0_0&ms=4',
		)

	def parse(self, response):
		items = []
		if 'item.jd.hk' in response.url:
			print '#'*50
			for parent,dirnames,filenames in os.walk(r'F:\git\jdcrawler\out\all'): 
				for filename in filenames:
					if filename not in crawled:
						p = filename[:-9]
						yield Request('http://club.jd.com/allconsultations/' + p + '-1-1.html', callback=self.parse)

		elif 'http://club.jd.com' in response.url and '.html' in response.url:
			body = response.body
			soup = bs(body,'html5lib',fromEncoding="gb18030")
			pid = response.url.split('/')[-1].split('-')[0]

			item = CrawlerItem()

			item['url'] = response.url

			item['title'] = self.getTitle(soup)
			# item['table2'] = str(soup.find('div', class_='Refer_List'))

			count , item['table2'] = self.getQA(soup, response.url)
			if pid in pairCount:
				pairCount[pid] += count
			else:
				pairCount[pid] = count

			item['table'] = ''
			item['need_know'] = ''
			item['faq'] = ''
			items.append(item)
			yield item

			if '-1-1' in response.url:
				pageCount = 1
				Pagination = soup.find('div', class_='Pagination')
				if Pagination!=None:
					pageCount = int(self.getPageCount(Pagination))
				print 'pageCount = ' + str(pageCount)
				for page in xrange(2, pageCount+1):
					yield Request('http://club.jd.com/allconsultations/' + pid + '-'+ str(page) +'-1.html', callback=self.parse)

	def getTitle(self, soup):
		titleBox = soup.find('div', id='itemInfo')
		if titleBox == None:
			title = soup.title.string.encode('utf-8')
		return title

	def getQA(self, soup ,url):
		Refer_List = soup.find('div', class_='Refer_List')
		count = 0
		if Refer_List == None:
			detail = 'Refer_List None'
		else:
			kv = {}
			Refer_s = Refer_List.find_all(has_refer)
			c = 0
			kv['len'] = len(Refer_s)
			for refer in Refer_s:
				pair = {}
				r_info = refer.find('div', class_='r_info')
				t = getListSingle(r_info)
				pair['time'] = t[-1].replace('\n','').replace('\t','').replace('\r','').replace(' ','')

				ask = refer.find('dl', class_='ask')
				dd_ask = ask.find('dd').find('a')
				pair['ask'] = dd_ask.string.replace('\n','').replace('\t','').replace('\r','').replace(' ','')

				answer = refer.find('dl', class_='answer')
				dd_answer = answer.find('dd')
				pair['answer'] = dd_answer.string.replace('\n','').replace('\t','').replace('\r','').replace(' ','')
				kv[c] = pair
				c+=1
			detail = json.dumps(kv,ensure_ascii=False).encode("utf-8")
		return count, detail

	def getPageCount(self, pagediv):
		a_s = pagediv.find_all('a')
		if len(a_s)>=2:
			return int(a_s[-2].string)
		return 1

		