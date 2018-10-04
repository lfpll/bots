from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


chrome_options = Options()  
chrome_options.add_argument("--headless")  
driver = webdriver.Chrome()  
driver.get('https://3eonline.com/WebInsight/Default.aspx')
actionChains = ActionChains(driver)
wait = WebDriverWait(driver, 10)

def login(login_xpath,pass_xpath,login,passwd,driver = driver):
	login_elem = driver.find_element_by_css_selector(login_xpath)
	login_elem.send_keys(login)
	pass_elem = driver.find_element_by_css_selector(pass_xpath)
	pass_elem.send_keys(passwd)
	pass_elem.send_keys(Keys.ENTER)

login('#LoginView1_Login1_UserName','#LoginView1_Login1_Password','luiz.lobo@exxonmobil.com','Luiz2812*')

# Find and element by the text inside
def elem_by_text(element,text,driver=driver):
	try:
		elem_wait = wait.until(EC.presence_of_element_located((By.XPATH, '//%s[text()="%s"]'%(element,text))))
	except Exception as e:
		raise(e)
	return driver.find_element(By.XPATH, '//%s[text()="%s"]'%(element,text))

# Assuming there is only one element visible with the text
def elem_by_text_visible(element,text,driver=driver):
	try:
		elem_wait = wait.until(EC.presence_of_element_located((By.XPATH, '//%s[text()="%s"]'%(element,text))))
	except Exception as e:
		raise(e)_
	return list(filter(lambda elem:len(elem.text) > 0,driver.find_elements(By.XPATH, '//%s[text()="%s"]'%(element,text))))

# Double click in a element
def double_click(element,driver=driver):
	return actionChains.double_click(element).perform()

def set
cookies = driver.get_cookies()


