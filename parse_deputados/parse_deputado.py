import requests
from bs4 import BeautifulSoup
from insert_mdb import con_mdb
import re

school_re = re.compile('Escolaridade')
deputados 	= con_mdb('Political','deputados')


def get_page(url):
	page = requests.get(url)
	return BeautifulSoup(page.text,'lxml')

# Div soup parent object
def get_href_text(aTag):
	return {'url':aTag['href'].strip(),'text':aTag.text.strip()}


# Return the last children(s) div of the divs
def get_last_div(div):
	div_list = div.findChildren('div')
	return [div for div in div_list if len(div.find_all('div')) == 0]

# Find all the urls inside the element with text
def find_all_urls(soup_element):
	a_list = soup_element.find_all('a')
	return [{'url':a['href'],'text':a.text.strip()} for a in a_list]
		
# Return political name and party 
def get_name_party(page_obj,div_parent):
	name_party	 = div_parent.find('div',{'class':'bioNomParlamentrPartido'}).text.strip().split('-')
	page_obj	= {'nickname':name_party[0].strip(),'party':name_party[1].strip()}	 
	return page_obj


#	Return general info like age,real name, scolarity and parents.
def get_general_info(page_obj,div_parent):
	
	detal = div_parent.find('div',{'class':'bioDetalhes'})
	strongs = detal.find_all('strong')
	spans = detal.find_all('span')
	page_obj['name'] = strongs[0].text.strip().replace('\n','')
	for span,strong in zip(spans,strongs[1:]):
		if school_re.search(span.text):
			page_obj['Escolaridade'] = strong.text.replace('\n','').strip()
		else:
			page_obj[span.text.strip().replace(':','')] = strong.text.replace('\n','').strip()
	return page_obj



def check_hrefs(element):
	return True if element.find('a') is not None else False

def check_reference(element):
	text = element.text
	# Check if is the last word is ':'
	if text.find(':')>0:
		return True
	else:
		return False

def get_page_politician(url):

	soup 		= get_page(url)
	page_obj 	= get_name_party({},soup)
	page_obj['url'] = url
	page_obj  	= get_general_info(page_obj,soup)
	div_bio		= soup.select('.bioOutros')

	for div_element in div_bio:
		# Elements that have their names and find_all_urls
		if check_hrefs(div_element) and check_reference(div_element):
			page_obj[div_element.text.strip().split(':')[0]] = [{a.text.strip():a['href']} for a in div_element.find_all('a')] 
		# Find elements that have their names and urls at the same
		elif check_hrefs(div_element):
			a_list = div_element.find_all('a')
			for a in a_list:
				page_obj[a.text.strip()] = a['href']
		# Elements that have names and text
		elif check_reference(div_element):
			text_array = div_element.text.replace('\n','').strip().split(':')
			page_obj[text_array[0]] = ''.join(text_array[1:]).strip().replace('  ','')
	
	deputados.insert(page_obj)
