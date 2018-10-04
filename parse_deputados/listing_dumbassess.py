from parse_deputado import get_page_politician
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from insert_mdb import con_mdb


deputados   = con_mdb('Political','deputados')
last_deput 	= deputados.find().count()

chrome_options = Options()  
chrome_options.add_argument("--headless")  
driver = webdriver.Chrome(chrome_options=chrome_options)  
driver.get('http://www2.camara.leg.br/deputados/pesquisa')
wait = WebDriverWait(driver, 10)


# Return the list of the options in the website selector removing the first option
def options_list(x_prop,rm_first = False):
	elem_wait = wait.until(EC.presence_of_element_located((By.XPATH, x_prop)))
	options = driver.find_element_by_xpath(x_prop)
	elem_wait = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,'option')))
	return options.find_elements_by_css_selector('option')[1:] if rm_first else options.find_elements_by_css_selector('option')
	

# Return the url of the page
def get_urls(option):
	option.click()
	print(option.text)
	driver.find_element_by_css_selector('#rbDeputado8').click()
	driver.find_element_by_css_selector('#Pesquisa').click()
	return driver.current_url


# Click on the options of the website 
# If error at the selection, select the same option
def recursive_clicking(options_array = options_list('//*[@id="deputado"]'),i =0):
	options_array = options_list('//*[@id="deputado"]')[1:]
	# Do the process of clicking in the deputy
	if len(options_array) == i:
		return 
	get_page_politician(get_urls(options_array[i]))
	driver.back()
	i = i+1
	recursive_clicking(i=i)


recursive_clicking(i=last_deput)