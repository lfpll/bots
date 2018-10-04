from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from pymongo import InsertOne
import requests
from bs4 import BeautifulSoup
from lxml import html
from multiprocessing import Pool
import itertools
import re


client_world = MongoClient()

# Get the url of the proposes
deputados   = list(client_world['Political']['deputados'].find({},{'Proposições de Autoria do Deputado':1}))
# Get the ids of the deputys that were already parsed
ids_parsed = list(client_world['Political']['laws'].distinct('deputy'))

# Some global variables needed for parsing and joining
prox=re.compile("próxima")
relative_url = 'http://www.camara.leg.br'

# Return all the laws from the deputy
def deliver_laws(_id,page,laws = []):

	# Parse each tbody block of the page and return object of the data parsed
	def parse_tbody(soup,_id):

		a 	   = soup.find('a',attrs={'class':['rightIconified','iconDetalhe']})
		l_nam  = a.text.strip()
		l_url  = a['href']
		para   	= soup.find_all('p')
		em_dat 	= para[1].text.replace('Ementa','').replace('Data de apresentação:','').split(':')
		autor 	= para[0].text.split(':')[1].strip().replace('.','')
		situ 	= soup.find_all('td')[2].text.strip()
		despa 	= soup.text.split('\n')[-1]
		ementa 	= em_dat[1].strip()
		data   	= em_dat[0].strip()


		return {'deputy':_id,'codigo':l_nam,'url':l_url,'situation':situ,'authors':autor,'ementa':ementa,'data':data,'despacho':despa}


	# Parse page with list of laws
	def parse_page(_id,soup):
		
		tbodys = soup.find_all('tbody',class_='coresAlternadas')
		laws   = list(map(lambda sp:parse_tbody(sp,_id=_id),tbodys))
		if len(tbodys) != len(laws): print('wrong values')

		return laws

	soup   = BeautifulSoup(page.text,'lxml')
	laws_parsed = parse_page(soup=soup,_id=_id)
	laws.extend(laws_parsed)
	url    = soup.find_all('a',text=prox)

	# Check if it is the last page
	if (len(url)>0):
		page = confirm_page(relative_url+url[0].get('href'))
		return deliver_laws(_id=_id,page=page,laws=laws)
	else:
		return laws

# Inserting a lot of values inside a mongodb database
# Recursive if there is any problems ( Not recommended)
client = MongoClient()
def insert_values(laws):

	laws_collections = client['Political']['laws']
	try:
		laws_collections.bulk_write(laws)
	except BulkWriteError as e:
		print(e.details)
		exit()
		insert_values(laws)
	return

# Check if page was correctly loaded
# Reload if not
def confirm_page(url):
	page = requests.get(url)
	print(url)
	if page.status_code == 200:
		return page
	else:
		return confirm_page(url)


# Iterate through the deputys and insert the laws
def db_iterate(dep_obj):
	url,_id = dep_obj['Proposições de Autoria do Deputado'],dep_obj['_id']
	# Check if the id of the deputy was already parsed
	if _id in ids_parsed:
		print('%s inside'%_id)
		return
	else:
		page = confirm_page(url)
		laws = deliver_laws(_id=_id,page=page)
		laws = [InsertOne(law) for law in laws]
		client = MongoClient()
		laws_collections = client['Political']['laws']
		laws_collections.bulk_write(laws)
		client.close()
		print('%s Inserted'%_id)



with Pool(4) as p:
	p.map(db_iterate,deputados)


