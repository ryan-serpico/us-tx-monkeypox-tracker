import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def getPage():
    monkeypox_website = 'https://www.cdc.gov/poxvirus/monkeypox/response/2022/us-map.html'

    # Create an options object to set the headless browser
    options = Options()
    options.headless = True

    driver = webdriver.Firefox(service=Service(executable_path='driver/ubuntu/geckodriver'), options=options)
    # driver = webdriver.Firefox(service=Service(executable_path='driver/geckodriver'), options=options)

    driver.get(monkeypox_website)

    # Wait until an a tag with the classes theme-blue btn btn-download no-border is loaded
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'btn-download')))
    
    return driver.page_source

def updateTexas(df):
    # Rename the first column of the dataframe to 'State' and the second to 'Count'
    us_cdc_table.columns = ['State', 'Count']

    # Filter the dataframe for just Texas
    texas_df = us_cdc_table[us_cdc_table['State'] == 'Texas']

    # Get the latest count for Texas
    texas_latest = texas_df.iloc[0]['Count']

    # Print today's date
    date = datetime.datetime.now().strftime("%-m/%-d/%y")

    data = {'Date': [date], 'Count': [texas_latest]}

    new_data =  pd.DataFrame(data)
    old_data_df = pd.read_csv('data/texas_data.csv')
    updated_df = pd.concat([old_data_df, new_data])
    updated_df.to_csv('data/texas_data.csv', index=False)

def getTexasPhrData():
    df = pd.read_html('https://dshs.texas.gov/news/updates.shtm#monkeypox')[0].iloc[:-1]

    # Find and replace any instance of "PHR " in the "Public Health Region" with nothing.
    df['Public Health Region'] = df['Public Health Region'].str.replace('PHR ', '')

    df.to_csv('data/texas_phr_data.csv', index=False)

def getBexarCases():
    url = 'https://www.sanantonio.gov/health/news/alerts/monkeypox'
    page = requests.get(url)    
    soup = BeautifulSoup(page.content, 'html.parser')
    print('Getting Bexar cases...')
    bexar_cases = soup.find('div', class_='alert alert-error alert-block fade in').find_all('strong')[1].next_sibling.strip().replace(': ', '')
    bexar_cases = int(bexar_cases)

    # Print today's date
    date = datetime.datetime.now().strftime("%-m/%-d/%y")

    data = {'Date': [date], 'Count': [bexar_cases]}

    new_data =  pd.DataFrame(data)
    old_data_df = pd.read_csv('data/bexar_log.csv')
    updated_df = pd.concat([old_data_df, new_data])
    updated_df.to_csv('data/bexar_log.csv', index=False)

    # Get the second to last value from the "Count" column in the bexar_log.csv file
    try:
        bexar_cases_last = pd.read_csv('data/bexar_log.csv').iloc[-2]['Count']
        new_cases = bexar_cases - bexar_cases_last
    except:
        new_cases = 0   
    

    df = pd.DataFrame(
        {'All time': [bexar_cases],
        'New': ['+' + str(new_cases)]})

    df.to_csv('data/bexar_table.csv', index=False)

def getHarrisCases():
    print('Getting Harris cases...') 
    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
        }
    url = 'https://publichealth.harriscountytx.gov/monkeypox'
    r = requests.get(url, headers=header)
    df = pd.read_html(r.text)[0]

    # Get the first value from the "City of Houston" column
    harris_cases = df.iloc[0]['City of Houston']
    uninc_cases = df.iloc[0]['Unincorporated Harris County']

    date = datetime.datetime.now().strftime("%-m/%-d/%y")
    data = {'Date': [date], 'Harris County Count': [harris_cases], 'Unincorporated Harris County Count': [uninc_cases]}

    new_data =  pd.DataFrame(data)
    old_data_df = pd.read_csv('data/harris_log.csv')
    updated_df = pd.concat([old_data_df, new_data])
    updated_df.to_csv('data/harris_log.csv', index=False)

    try:
        harris_cases_last = pd.read_csv('data/harris_log.csv').iloc[-2]['Harris County Count']
        uninc_cases_last = pd.read_csv('data/harris_log.csv').iloc[-2]['Unincorporated Harris County Count']

        harris_cases_new = harris_cases - harris_cases_last
        uninc_cases_new = uninc_cases - uninc_cases_last
    except:
        harris_cases_new = 0
        uninc_cases_new = 0


    table_df = pd.DataFrame({
        '': ['Harris County', 'Unincorporated Harris County'],
        'All time': [harris_cases, uninc_cases],
        'New': ['+' + str(harris_cases_new), '+' + str(uninc_cases_new)]
    })

    table_df.to_csv('data/harris_table.csv', index=False)

cdc_page = getPage()

us_cdc_table = pd.read_html(cdc_page)[0]

us_cdc_table.to_csv('data/us_cdc_table.csv', index=False)

updateTexas(us_cdc_table)

getTexasPhrData()

getBexarCases()
getHarrisCases()
