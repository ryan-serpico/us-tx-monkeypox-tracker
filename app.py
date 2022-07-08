import datetime

import pandas as pd
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

    driver = webdriver.Firefox(service=Service(executable_path='driver/geckodriver'), options=options)

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

cdc_page = getPage()

us_cdc_table = pd.read_html(cdc_page)[0]

us_cdc_table.to_csv('data/us_cdc_table.csv', index=False)

updateTexas(us_cdc_table)


