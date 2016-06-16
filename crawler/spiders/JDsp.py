# -*- coding: utf-8 -*-
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
	name = "JDsp"
	allowed_domains = ['jd.com', 'jd.hk']

	for parent,dirnames,filenames in os.walk(r'F:\git\jdcrawler\out\ed'): 
		for filename in filenames:
			crawled.add(filename.strip())
	
	start_urls = (
		# 'http://item.jd.hk/1957483655.html',
		# 'http://item.jd.hk/10345569383.html',
		'http://www.jd.hk/',
		# 'http://item.jd.com/10228033653.html',
		# 'http://list.jd.com/list.html?cat=9987,653,655&page=1&go=0&JL=6_0_0&ms=4',
		)

	def parse(self, response):
		items = []
		if 'list.html' in response.url:
			values = {'cat':'9987,653,655',\
			'page':1,\
			'go':0,\
			'JL' : '6_0_0',\
			'ms':4,}		

			allphones = ''
			for i in range(beginWith, totalPages):
				values['page'] = i
				body = get('http://list.jd.com/list.html', values)
				findPhone = re.compile('item.jd.com/\d+.html')
				phones = findPhone.findall(body)
				# allphones += '\n'.join(p for p in phones) +''

			# item = CrawlerItem()
			# item['url'] = response.url
			# item['title'] = 'allphones'
			# item['table2'] = str(crawled)
			# item['table'] = ''
			# item['need_know'] = ''
			# item['faq'] = ''
			# items.append(item)
			# yield item
				for p in phones:
					pid = p.split('/')[-1]+'.txt'
					if pid not in crawled:
						yield Request('http://' + p, callback=self.parse)

		elif 'www.jd.hk' in response.url:
			for parent,dirnames,filenames in os.walk(r'F:\git\jdcrawler\out\hk'): 
				for filename in filenames:
					if filename not in crawled:
						p = filename[:-4]
						yield Request('http://item.jd.hk/' + p, callback=self.parse)

		elif 'item.jd.hk' in response.url:
			body = response.body
			soup = bs(body,'html5lib')
			item = CrawlerItem()
			item['url'] = response.url

			item['title'] = self.getTitle(soup)

			item['table2'] = self.getDetail_HK(soup, response.url)

			item['table'] = ''
			item['need_know'] = ''
			item['faq'] = ''
			items.append(item)
			yield item

		elif 'item.jd.com' in response.url:
			body = response.body
			soup = bs(body,'html5lib')
			item = CrawlerItem()
			item['url'] = response.url

			item['title'] = self.getTitle(soup)

			item['table2'] = self.getDetail(soup, response.url)
			if 'None' in item['table2']:
				item['table2'] = 'getDetail None'

			item['table'] = ''
			item['need_know'] = ''
			item['faq'] = ''
			items.append(item)
			yield item
		else:			
			body = response.body
			soup = bs(body,'html5lib')
			item = CrawlerItem()
			item['url'] = response.url

			item['title'] = self.getTitle(soup)

			item['table2'] = ''

			item['table'] = ''
			item['need_know'] = ''
			item['faq'] = ''
			items.append(item)
			yield item

	def getTitle(self, soup):
		titleBox = soup.find('div', id='itemInfo')
		if titleBox == None:
			title = soup.title.string.decode('unicode').encode('utf-8')
		else:
			ttitle = titleBox.find('div' , id='name')
			title = getListString(ttitle)
		return title

	def getDetail(self, soup ,url):
		detailBox = soup.find('div', id='product-detail-2')
		if detailBox == None:
			detailBox = soup.find('div', class_='ui-switchable-panel mc hide')
		if detailBox == None:
			detail = 'detailBox None'
		else:
			kv = {}
			kv['price'] = self.getPrice(soup,url)
			table = detailBox.find('table')
			if table == None:
				return 'table None'
			# tbody = table.find('tbody')
			# if tbody == None:
			# 	return 'tbody None'
			tr_s = table.find_all('tr')
			for tr in tr_s:
				td_s = getListSingle(tr)
				if td_s==None:
					continue
				elif len(td_s) >=2:
					kv[td_s[0]] = ' '.join(t for t in td_s[1:])
			detail = json.dumps(kv,ensure_ascii=False).encode('utf-8')
		return detail

	def getDetail_HK(self, soup ,url):
		detailBox = soup.find('div', id='detail-param')
		if detailBox !=None:
			kv = {}
			kv['price'] = self.getPrice(soup,url)
			table = detailBox.find('table')
			if table == None:
				return 'table None'
			tr_s = table.find_all('tr')
			for tr in tr_s:
				td_s = getListSingle(tr)
				if td_s==None:
					kv['ERROR========'] = '============'
				elif len(td_s) >=2:
					kv[td_s[0]] = ' '.join(t for t in td_s[1:])
			detail = json.dumps(kv,ensure_ascii=False).encode('utf-8')
			return detail

		if detailBox ==None:
			detailBox = soup.find('div', class_='p-parameter')
			if detailBox != None:
				kv = {}
				ul_s = detailBox.find_all('ul')
				for ul in ul_s:
					li_s = ul.find_all('li')
					for li in li_s:
						liString = getListSingle(li)
						if liString==None:
							continue
						elif len(liString) >1:
							k = liString[0].replace('：','')
							kv[k] = ' '.join(t for t in liString[1:])
						elif '：' in liString[0]:
							k,v = liString[0].split('：')
							kv[k] = v
					detail = json.dumps(kv,ensure_ascii=False).encode('utf-8')
				return detail




		if detailBox ==None:		
			detailBox = soup.find('ul', class_='p-parameter-list')
		if detailBox == None:
			detailBox = soup.find('ul', id='parameter2')
		if detailBox == None:
			detail = 'detailBox None 2'
		else:
			kv = {}
			kv['price'] = self.getPrice(soup,url)
			li_s = detailBox.find_all('li')
			for li in li_s:
				liString = getListSingle(li)
				if liString==None:
					continue
				elif len(liString) >1:
					k = liString[0].replace('：','')
					kv[k] = ' '.join(t for t in liString[1:])
				elif '：' in liString[0]:
					k,v = liString[0].split('：')
					kv[k] = v
			detail = json.dumps(kv,ensure_ascii=False).encode('utf-8')
		return detail

	def getPrice(self, soup,url):
		pid = url.split('/')[-1].split('.')[0]
		val = {
			'skuid':'J_'+pid,
			'callback':'cnp'
		}
		res = get('http://p.3.cn/prices/get', val)
		getP = re.compile('\\"p\\":\\\"(\d+\.\d+)\\\"')
		t = getP.findall(res)
		if t==None or len(t)<1:
			return 'None'
		return t[0]
		