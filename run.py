#!/usr/bin/python
import smtplib
import requests
import time
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import COMMASPACE, formatdate
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# RECEIPIENTS = ['dong.lenny@gmail.com', 'michael.chen@berkeley.edu', 'acdelapaz@berkeley.edu']
RECEIPIENTS = ['dong.lenny@gmail.com']

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
        floor_plan = floor_plan.find_all('img')[0]['src'][:-3] + '500'

        for unit in units:
            apartment_number = unit.find_all('td')[1].text
            move_in = unit.find_all('td')[2].text
            price = unit.find_all('span', {'class': 'new-price'})[0].text

            listing = Listing('Avalon', bedrooms, price, size, datetime.strptime(move_in, '%m/%d/%Y'), floor_plan, apartment_number)
            listings.append(listing)

    return listings

def get_beale():
    listing_obj = []
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('headless')
    chrome_options.add_argument('no-sandbox')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    root = 'https://www.udr.com'
    driver.get('{0}/san-francisco-bay-area-apartments/san-francisco/388-beale/apartments-pricing/?beds=2'.format(root))
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.close()

    all_listings = soup.find(id='listings-a')
    listings = all_listings.findChildren()[0].find_all('li', recursive=False)

    for listing in listings:
        attributes = listing.findChildren()[0].find_all('li', recursive=False)
        floor_plan = '{0}{1}'.format(root, attributes[0]['data-zoom-src'])
        apartment_number = 'Apartment {0}'.format(attributes[1].find('h3').text.split('Apartment ')[1])
        bedrooms = 2
        size = '{0} Sq. Ft.'.format(attributes[1].find_all('li')[2].text.split('Sq. Ft: ')[1])
        price = attributes[2].find('li', {'class': 'price'}).find_all('div')[1].find('span').find('span').text
        date = attributes[2].find('li', {'class': 'available'}).find_all('div')[1].find('span').text
        if date.lower() == 'now':
            date = datetime.now()
        else:
            date = datetime.strptime(date, '%m/%d/%Y')
        listing_obj.append(Listing('Beale', bedrooms, price, size, date, floor_plan, apartment_number))

    return listing_obj

def get_edgewater():
    listing_obj = []
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('headless')
    chrome_options.add_argument('no-sandbox')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    root = 'https://www.udr.com'
    driver.get('{0}/san-francisco-bay-area-apartments/san-francisco/edgewater/apartments-pricing/?beds=2'.format(root))
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.close()

    all_listings = soup.find(id='listings-a')
    listings = all_listings.findChildren()[0].find_all('li', recursive=False)

    for listing in listings:
        attributes = listing.findChildren()[0].find_all('li', recursive=False)
        floor_plan = '{0}{1}'.format(root, attributes[0]['data-zoom-src'])
        apartment_number = 'Apartment {0}'.format(attributes[1].find('h3').text.split('Apartment ')[1])
        bedrooms = 2
        size = '{0} Sq. Ft.'.format(attributes[1].find_all('li')[2].text.split('Sq. Ft: ')[1])
        price = attributes[2].find('li', {'class': 'price'}).find_all('div')[1].find('span').find('span').text
        date = attributes[2].find('li', {'class': 'available'}).find_all('div')[1].find('span').text
        if date.lower() == 'now':
            date = datetime.now()
        else:
            date = datetime.strptime(date, '%m/%d/%Y')
        listing_obj.append(Listing('Edgewater', bedrooms, price, size, date, floor_plan, apartment_number))

    return listing_obj

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

    msg_root = MIMEMultipart('related')
    msg_root['From'] = send_from
    msg_root['To'] = COMMASPACE.join(RECEIPIENTS)
    msg_root['Date'] = formatdate(localtime=True)
    msg_root['Subject'] = subject
    msg_root.preamble = 'This is a multi-part message in MIME format.'

    msg_alternative = MIMEMultipart('alternative')
    msg_root.attach(msg_alternative)

    msg_text = MIMEText('This is the alternative plain text message.')
    msg_alternative.attach(msg_text)

    msg_text = MIMEText(content, 'html')
    msg_alternative.attach(msg_text)

    server.sendmail(send_from, ['dong.lenny@gmail.com'], msg_root.as_string())
    server.close()


class Listing:
    def __init__(self, company, bedrooms, price, size, move_in, floor_plan, apartment_number):
        self.floor_plan = floor_plan.replace(' ', '%20')
        self.price = price
        self.bedrooms = bedrooms
        self.move_in = move_in
        self.size = size
        self.company = company
        self.apartment_number = apartment_number

    def __str__(self):
        return '<h2>{0}</h2><big>{6}</big><br><big>{1} Bedrooms</big><br><big>{2}</big><br><big>{3}</big><br><big>Move-in date: {4}</big><br><img src="{5}">'.format(self.company, self.bedrooms, self.price, self.size, self.move_in.strftime('%m/%d/%Y'), self.floor_plan, self.apartment_number)

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

def package_and_send(fetch, company):
    listings = fetch()
    listings.sort(key=lambda x: x.move_in, reverse=True)

    content = ''
    for listing in listings:
        content += str(listing)
        content += '<br><br><br>'

    send_mail('Available {1} apartments as of {0}'.format(datetime.now().strftime('%m/%d/%Y'), company), content)
    print '{0} finished'.format(company)


# avalon_listings = get_avalon()
#
# avalon_listings.sort(key=lambda x: x.move_in, reverse=True)
#
# content = ''
# for listing in avalon_listings:
#     content += str(listing)
#     content += '<br><br><br>'

# send_mail('Available apartments as of {0}'.format(datetime.now().strftime('%m/%d/%Y')), content)

package_and_send(get_avalon, 'Avalon')
package_and_send(get_beale, 'Beale')
package_and_send(get_edgewater, 'Edgewater')

f = open('last_run', 'w')
f.write('{0}\n'.format(str(datetime.now())))
f.close()
