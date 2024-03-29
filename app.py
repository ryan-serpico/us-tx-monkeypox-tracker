import datetime
import json

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

def getTexasAgeData():
    df = pd.read_html('https://dshs.texas.gov/news/updates.shtm#monkeypox')[1].iloc[:-1]

    df.to_csv('data/texas_age_data.csv', index=False)

def getTexasSexData():
    df = pd.read_html('https://dshs.texas.gov/news/updates.shtm#monkeypox')[2].iloc[:-1]

    df.to_csv('data/texas_sex_data.csv', index=False)

def getTexasSevenDayAverages():
    df = pd.read_csv('data/texas_data.csv')
    df['New cases'] = df['Count'] - df['Count'].shift(1)
    df['7-day average'] = round(df['New cases'].rolling(7).mean(), 1)
    df['Baseline'] = 0
    df = df.dropna()
    # If a value in the "New cases" column is negative, set it to 0
    df['New cases'] = df['New cases'].apply(lambda x: 0 if x < 0 else x)
    df.to_csv('data/texas_seven_day_averages.csv', index=False)

def createMetadata():
    print('Creating metadata...')
    # Save current date to variable in this format: Aug. 4, 2022
    date = datetime.datetime.now().strftime("%b. %-d, %Y")
    s = f'Data as of {date}'
    data = {}
    
    # Create nested dictionary with metadata
    data['annotate'] = {'notes': s}

    json_data = json.dumps(data)
    with open('data/metadata.json', 'w') as f:
        f.write(json_data)

cdc_page = getPage()

us_cdc_table = pd.read_html(cdc_page)[0]

us_cdc_table.to_csv('data/us_cdc_table.csv', index=False)

updateTexas(us_cdc_table)
getTexasPhrData()
getBexarCases()
getTexasAgeData()
getTexasSexData()
getTexasSevenDayAverages()
createMetadata()
