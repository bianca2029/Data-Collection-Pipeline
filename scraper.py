from distutils.errors import LinkError
import json
from lib2to3.pgen2 import driver
from operator import index
from re import search
import tempfile
from unicodedata import name
from urllib import response
from urllib.parse import urljoin
from xml.etree.ElementPath import xpath_tokenizer
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from bs4  import BeautifulSoup
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
import uuid
import time
import urllib.request
import requests
import boto3
import tempfile
#import pandas as pd
from tqdm import tqdm
#from sqlalchemy import create_engine
import os
import lxml

class Scraper:
    '''
    This class is used to represent  web scraping of a website

    Attributes:
        accept_cokies: accept cookies of the website
        write_address: address of the location
        write_in_search_bar: category wanted
        iteratre_through_list: the list of the restaurants
        get_restaurant_details: The details of the restaurants
    ''' 
    def __init__(self, url):
        '''
        Constructs all the necessary attributes for the scriper object.

        Parameters
        ----------
            url: url
                URL of the website
            
        '''
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--allow-running-insecure-content')        
        chrome_options.add_argument('--no-sandbox')        
        chrome_options.add_argument('--headless')        
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'") 
        chrome_options.add_argument("window-size=1920,1080") 
        self.url = url
        self.driver = Chrome(ChromeDriverManager().install(), options=chrome_options) 
        self.driver.get(self.url)
        
        # DATABASE_TYPE = 'postgresql'
        # DBAPI = 'psycopg2'
        # HOST = ''
        # USER = 'postgres'
        # PASSWORD = 'postgres'
        # DATABASE = 'postgres'
        # PORT = '5432'
        self.key_id = input('Add AWS key_id: ') 
        self.secret_key = input('Add AWS secret_key: ') 
        self.region =input('Add the AWS region: ') 
       
        self.client = boto3.client(
            's3',
            aws_access_key_id = self.key_id,
            aws_secret_access_key = self.secret_key,
            region_name = self.region
        )

        #self.engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

        self.data_store= "./raw_data"
        self.create_store(self.data_store)

    def accept_cookies(self, xpath, iframe = None):
        '''
        This function accept the cookies button of the website
        If is added an xpath the cookie button will be clicked
        
        Parameters
        ------------
        xpath: str
            xpath of the accept cookie button
        iframe: optional
            if the website has an iframe
        -----------

        Returns
            driver
        '''
        try:
            time.sleep(2)
            self.driver.switch_to.frame(iframe)
            cookies_button = (
                 WebDriverWait(self.driver, 10)
                .until(EC.presence_of_element_located((
                    By.XPATH, xpath))
                    )
            )
            cookies_button.click()
        except AttributeError:
            self.driver.switch_to.frame(iframe)
            cookies_button = (
                 WebDriverWait(self.driver, 10)
                .until(EC.presence_of_element_located((
                    By.XPATH, xpath))
                    )
            )
            cookies_button.click()
        except:
            print('There was no cookies button.')
        return driver
   
    def click_address(self, xpath):
        '''
        This function click into the search bar address

        Parameters
        -----------
         xpath: str
            xpath of the search bar
        ---------
        '''
        time.sleep(2)
        address= self.driver.find_element(By.XPATH, xpath)
        address.click()
        return address

    def write_in_address(self, xpath:str ) -> None:
        '''
        This function allow us to write into the search bar of address

        Parameters
        ----------
        text: str
            The address
        xapth: str
            xapth of the search bar
        ------------
        '''
        time.sleep(1)
        address = self.click_search_bar(xpath) 
        your_address = input('Enter your delivery address: ')
        address.send_keys(your_address)
        
    def search(self, xpath):
        '''
        This function search after the address added

        Parameters
        --------
        xapth: str
            xapth of the search button 
        --------    
        '''
        time.sleep(1)
        search = self.driver.find_element(By.XPATH, xpath)
        search.click()
       
    def pop_up(self, xpath):
        '''
        This function accept the pop up of the website
        If the website not have the pop up will be printed a message

        Parameters
        ------------
        xpath: str
            xpath of pop up button
        --------
        '''
        try:
            time.sleep(5)
            pop_up = self.driver.find_element(By.XPATH, xpath)
            pop_up.click()  
        except AttributeError:
            pop_up = self.driver.find_element(By.XPATH, xpath)
            pop_up.click()
        except:
            print('There was no pop up button.')

    def click_search_bar(self, xpath):
        '''
        This function click into the food search bar 

        Parameters
        --------
        xpath: str
            xpath of the food search bar
        ---------
        
        Returns
            search bar variable

        '''
        time.sleep(2)
        search_bar = self.driver.find_element(By.XPATH, xpath)
        search_bar.click()
        return search_bar

    def write_in_search_bar(self, xpath:str ) -> None:
        '''
        This function write into the search bar a category

        Parameters
        ----------
        text: str
            The category wanted
        xpath: str
            The xpath of the search bar 
        ---------
        '''
        time.sleep(2)
        search_bar = self.click_search_bar(xpath)
        type_food = input('Enter you meal type:')
        search_bar.send_keys(type_food)
            
    def click_after(self, xpath):
        '''
        This function do the search after the category wanted

        Parameters
        ----------
        xpath: str
            xpath of first category appered under the search bar
        ---------
        '''
        time.sleep(2)
        search_bar = self.driver.find_element(By.XPATH, xpath)
        search_bar.click()
        time.sleep(1)
        current_url = self.driver.current_url
        return current_url

class ScraperDeliveroo(Scraper):
    '''
    Scraper that works only for the deliveroo website
    It will extract information about the name, category, time to delivery,
    in a certain location
    '''
    def __init__(self, url):
        super().__init__('https://deliveroo.co.uk/')
        self.restaurant_dict = {
            'ID': [],
            'Name': [],
            'Distance': [],
            'Delivery_time': [],
            'Category': [],
            'Friendly_ID' :[],
        }
        self.image_dict = {
            'ID': [],
            'Restaurant_ID': [],
            'Image_Link': [],
        }
        #df_restaurants = pd.DataFrame(self.restaurant_dict)
        #self.df = pd.read_sql('restaurants', self.engine)
        #self.friendly_id_scraped = list(self.df['Friendly_ID'])
        self.friendly_id_scraped =[]

    def go_to_address(self):
        self.accept_cookies(xpath="//button[@id='onetrust-accept-btn-handler']")
        self.write_in_address(
            '//*[@id="location-search"]')
        self.search("//button[@class='ccl-d0484b0360a2b432 ccl-233931c277401e86 ccl-ed9aadeaa18a9f19 ccl-a97a150ddadaa172']")
        self.pop_up("//button[@class='ccl-d0484b0360a2b432 ccl-233931c277401e86 ccl-ed9aadeaa18a9f19 ccl-a97a150ddadaa172']")

    def go_to_restaurants(self):
        time.sleep(1)
        self.write_in_search_bar('//div[@class="ccl-039ee28e826becac"]//input[@placeholder="Restaurants, groceries, dishes"]')
        time.sleep(1)
        self.click_after('//*[@id="__next"]/div/div/div[2]/div/div/div/div/div[1]/div/div/div[2]/div/div[1]/ul/li[1]/button')


    def get_links(self) -> list:
        link_list = []
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        for parent in soup.find_all(class_ ='HomeFeedGrid-b0432362335be7af'):
            a_tag = parent.find('a', class_ = 'HomeFeedUICard-3e299003014c14f9')
            base = 'https://deliveroo.co.uk'
            link = a_tag.attrs['href']
            url = urljoin(base, link)
            link_list.append(url)
        print(f'There are {len(link_list)} restaurants in this page')
        return link_list
        
    
    def get_info_in_link(self, link_list: list) -> None:
        time.sleep(1)
    
        for link in tqdm(link_list[:2]):
            list_of_words = link.split("/")
            name = list_of_words[6].split('?')
            friendly_id = name[0]
            if friendly_id in self.friendly_id_scraped:
                print(f'Already scraped {friendly_id} ' )
                continue
            else:
                self.driver.get(link)
                time.sleep(1)
                self.friendly_id_scraped.append(friendly_id)
                try:
                    name = self.driver.find_element(By.XPATH, '//*[@id="__next"]/div/div/div[3]/div/div/div/div[2]/h1').text
                except NoSuchElementException:
                    name = 'N/A'
                try:
                    distance = self.driver.find_element(By.XPATH, '//*[@id="__next"]/div/div/div[3]/div/div/div/div[2]/div[2]/p/span[9]').text
                except NoSuchElementException:
                    distance = 'N/A'
                try:
                    category = self.driver.find_element(By.XPATH, '//*[@id="__next"]/div/div/div[3]/div/div/div/div[2]/div[1]/p/span[3]').text
                except NoSuchElementException:
                    category = 'N/A'
                try:
                    delivery_time = self.driver.find_element(By.XPATH, '//*[@id="__next"]/div/div/div[3]/div/div/div/div[2]/div[1]/p/span[1]').text              
                except NoSuchElementException:
                    delivery_time = 'N/A'
                time.sleep(1)
                self.restaurant_dict['ID'].append(str(uuid.uuid4()))
                self.restaurant_dict['Name'].append(name)
                self.restaurant_dict['Distance'].append(distance)
                self.restaurant_dict['Delivery_time'].append(delivery_time)
                self.restaurant_dict['Category'].append(category)
                self.restaurant_dict['Friendly_ID'].append(friendly_id)
        
                try:
                    time.sleep(1)
                    image_list = []
                    soup = BeautifulSoup(self.driver.page_source, 'lxml')
                    for items in soup.find_all("div", {"class": "MenuHeader-f5663bee847582a6"}):
                        items = items.find('div')
                        image_url = items['style'].split('url("')[1].split('")')[0]
                        img_data = requests.get(image_url).content  
                        image_list.append(image_url)
                except NoSuchElementException:
                    image_list = []
        
                with tempfile.TemporaryDirectory() as tmpdirname:
                    for i in range (len(image_list)):
                        time.sleep(1)
                        new_id = str(uuid.uuid4())
                        urllib.request.urlretrieve(image_list[i], tmpdirname + f'/{new_id}.jpg')
                        self.client.upload_file(tmpdirname + f'/{new_id}.jpg', 'deliveroo-bucket', f'{new_id}.jpg')
                        self.image_dict['ID'].append(new_id)
                        self.image_dict['Restaurant_ID'].append(self.restaurant_dict['ID'][-1])
                        self.image_dict['Image_Link'].append(image_url)
                        print('images added')
        folder_name = input('Add the folder name: ')
        self.create_store(f'raw_data/{folder_name}') 
        time.sleep(2)
       
        self.data_dump(folder_name, self.restaurant_dict)               
        print(self.restaurant_dict)
        return self.restaurant_dict, self.image_dict
    def create_store(self, folder):
        '''
        This function create a new folder

        Parameters
        -----------
        folder:str
            the parent folder name 
        ------------
        '''
        time.sleep(1)
        if not os.path.exists(folder) :
            os.makedirs(folder)
        
    def data_dump(self, folder_name, data):
        '''
        This function dump the data collected into a JSON file

        Parameters
        -------
        folder_name: str
            the product folder 
        data: dict
            the dictionary with features product
        ---------
        '''
        with open(f"raw_data/{folder_name}/data.json", "w") as f:
            json.dump(data, f)
    # def create_table_restaurant(self, dict):
    #     time.sleep(1)
    #     df_restaurants = pd.DataFrame(self.restaurant_dict)
    #     df_restaurants.to_sql('restaurants', con = self.engine, if_exists='append')
    #     df_image = pd.DataFrame(self.image_dict)
    #     df_image.to_sql('images', con = self.engine, if_exists='append')

if __name__=='__main__':
    bot = ScraperDeliveroo('https://deliveroo.co.uk/')
    bot.go_to_address()
    time.sleep(1)
    bot.go_to_restaurants()
    time.sleep(2)
    links = bot.get_links()
    dict = bot.get_info_in_link(links)
    # bot.create_table_restaurant(dict)
   
