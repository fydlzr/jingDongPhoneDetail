# -*- coding: utf-8 -*-
from scrapy.exceptions import DropItem
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

class CrawlerPipeline(object):
	def __init__(self):
		self.urls_seen = set()
		self.taoCanMiaoShu_seen = set()

	def getOutputStr(self, item, slot=None, used_key=None):
		outputStr = ''
		keys = ['url','title','table','table2','need_know','faq']
		for k in keys:
			outputStr += '=====' + k + '=====\n'
			if k==slot and used_key!=None:
				newdict = {}
				jj = json.loads(item[k])
				for key in used_key:
					newdict[key] = jj[key]
				outputStr += json.dumps(newdict, ensure_ascii=False ).encode('utf-8') +'\n'
			else:
				outputStr += item[k].replace('\n','\t') +'\n'
		return outputStr

	def process_item(self, item, spider):
		if item['url'] in self.urls_seen:
			raise DropItem("Duplicate item found")
		# elif item['table'] 
		else:
			self.urls_seen.add(item['url'])

		if 'item' in item['url']:
			filename = 'out/phones/'  + item['url'].split('/')[-1]+'.txt'
			fout = open(filename,'wb')
			fout.write(self.getOutputStr(item))
			fout.close()
		elif 'list' in item['url']:
			fout = open('out/' + 'list.txt','w')
			fout.write(self.getOutputStr(item))
			fout.close()
		else:
			fout = open('out/' + item['url'].split('/')[-1]+'.txt','w')
			fout.write(self.getOutputStr(item))
			fout.close()

		return item
