#!/usr/bin/python
import smtplib
import requests
import time
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

RECEIPIENTS = ['dong.lenny@gmail.com', 'michael.chen@berkeley.edu', 'acdelapaz@berkeley.edu']

def get_avalon():
    listings = []
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('headless')
    chrome_options.add_argument('no-sandbox')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    # driver = webdriver.Chrome()
    driver.get('https://www.avaloncommunities.com/california/san-francisco-apartments/avalon-at-mission-bay/')
    time.sleep(5)
    elem_1 = driver.find_element_by_partial_link_text('Apartments + Pricing')
    elem_1.click()
    time.sleep(5)

    # WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CLASS_NAME, 'loading-overlay')))
    elem = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, '2 bedrooms')))
    elem.click()
    # new_elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'fa fa-caret-down')))

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.close()
    two_br = soup.find(id='bedrooms-2')
    two_br_floor_plans = two_br.find_all('div', {'class': 'floor-plan-listing'})[0]
    floor_plans = two_br_floor_plans.find_all('div', {'class': 'row'})

    for floor_plan in floor_plans:
        header = floor_plan.find_all('h4')[0]
        units = floor_plan.find_all('tr')[1:]
        header_text = header.text
        bedrooms = header_text.split(' bedrooms, ')[0]
        size = header_text.split('(')[1][:-2]
        floor_plan = floor_plan.find_all('img')[0]['src']

        for unit in units:
            move_in = unit.find_all('td')[2].text
            price = unit.find_all('span', {'class': 'new-price'})[0].text

            listing = Listing('Avalon', bedrooms, price, size, datetime.strptime(move_in, '%m/%d/%Y'), floor_plan)
            listings.append(listing)

    return listings


def wait_for(condition_function):
    start_time = time.time()
    while time.time() < start_time + 3:
        if condition_function():
            return True
        else:
            time.sleep(0.1)
    raise Exception(
        'Timeout waiting for {}'.format(condition_function.__name__)
    )

def send_mail(subject, content):

    send_from = 'afxdingdongassassin@gmail.com'
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(send_from, 'AfxDingDong')

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(RECEIPIENTS)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(content))

    server.sendmail(send_from, ['dong.lenny@gmail.com'], msg.as_string())
    server.close()

    print 'hello'

class Listing:
    def __init__(self, company, bedrooms, price, size, move_in, floor_plan):
        self.floor_plan = floor_plan
        self.price = price
        self.bedrooms = bedrooms
        self.move_in = move_in
        self.size = size
        self.company = company

    def __str__(self):
        return '{0}\n{1} Bedrooms\n{2}\n{3}\nmove-in date: {4}\n{5}'.format(self.company, self.bedrooms, self.price, self.size, self.move_in.strftime('%m/%d/%Y'), self.floor_plan)

    def __repr__(self):
        return '{0}, {1} Bedrooms, ${2}, {3} sq ft, move-in date: {4}'.format(self.company, self.bedrooms, self.price, self.size, self.move_in.strftime('%m/%d/%Y'))

class wait_for_page_load(object):

    def __init__(self, browser):
        self.browser = browser

    def __enter__(self):
        self.old_page = self.browser.find_element_by_tag_name('html')

    def page_has_loaded(self):
        new_page = self.browser.find_element_by_tag_name('html')
        return new_page.id != self.old_page.id

    def __exit__(self, *_):
        wait_for(self.page_has_loaded)



avalon_listings = get_avalon()

avalon_listings.sort(key=lambda x: x.move_in, reverse=True)

content = ''
for listing in avalon_listings:
    content += str(listing)
    content += '\n\n\n'

send_mail('Available apartments as of {0}'.format(datetime.now().strftime('%m/%d/%Y')), content)
