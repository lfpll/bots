from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from insert_mdb import con_mdb
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from time import sleep

chrome_options = Options()  
chrome_options.add_argument("--headless")  
driver = webdriver.Chrome()


def get_law(element,_id):
	a 	   = element.find_element_by_css_selector('a.rightIconified.iconDetalhe')
	# Law name and url
	l_nam  = a.get_attribute('text').strip()
	l_url  = a.get_attribute('href')
	
	# Law situation, author or authors and 	ement and date
	em_dat = element.find_element_by_xpath('//*[@id="frmListaProp"]/table/tbody[8]/tr[2]/td[2]/p[2]').text.split('\n')
	situ   = element.find_element_by_xpath('//*[@id="frmListaProp"]/table/tbody[1]/tr[1]/td[3]').text.strip()
	autor  = element.find_element_by_xpath('//*[@id="frmListaProp"]/table/tbody[1]/tr[2]/td[2]/p[1]').text.split(':')[1].strip()
	despa  = element.find_element_by_xpath('//*[@id="frmListaProp"]/table/tbody[1]/tr[2]/td[2]/b').text.split(':')[1].strip()
	ementa = em_dat[1].split(':')[1].strip()
	data   = em_dat[0].split(':')[1].strip()

	return {'deputy':_id,'codigo':l_nam,'url':l_url,'situation':situ,'authors':autor,'ementa':ementa,'data':data,'despacho':despa}

# Return all the laws
def get_data(_id,driver = driver):
	tbodys = driver.find_elements_by_css_selector('tbody.coresAlternadas')
	laws   = [get_law(law,_id=_id) for law in tbodys]
	return laws
		
# Click to next page button and get the laws
def deliver_laws(_id,driver = driver,laws = []):
	try:
		laws.extend(get_data(driver=driver,_id=_id))
		driver.get(driver.find_element_by_xpath('/html/body/div[2]/div/div/div/div/div[2]/form/div[2]/a[5]').get_attribute('href'))
		return deliver_laws(_id=_id,driver=driver,laws=laws)
	except Exception as e:
		return laws

# Get the value of the next deputy
def next_deputy(dep_conn):
	dep_obj = dep_conn.next()
	return dep_obj['Proposições de Autoria do Deputado'],str(dep_obj['_id'])

client_world = MongoClient()
deputados   = client_world['Political']['deputados'].find({},{'Proposições de Autoria do Deputado':1})
ids_in = list(client_world['Political']['laws'].distinct('deputy'))

# Inserting a lot of values inside
def insert_values(laws):
	try:
		client = MongoClient()
		client['Political']['laws'].insert_many(laws)
		client.close()
		return
	except BulkWriteError as e:
		print(laws)
		print(e.details)
		client.close()
		exit()
		print(e)
		insert_values(laws)

# Iterate through the deputys
def db_iterate(ids_in):
	url,_id = next_deputy(deputados)
	if _id in ids_in:
		print('%s inside'%_id)
		db_iterate(ids_in)
	else:
		driver.get(url)
		sleep(5)
		laws = deliver_laws(driver=driver,_id=_id)
		print('%s Inserted'%_id)
		insert_values(laws)
		db_iterate(ids_in)


db_iterate(ids_in)
driver.close()


