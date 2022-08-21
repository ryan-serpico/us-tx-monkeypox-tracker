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

def getHarrisCases():
    # url, headers, and body are all required to get data from powerbi
    url = 'https://wabi-us-gov-virginia-api.analysis.usgovcloudapi.net/public/reports/querydata?synchronous=true'

    headers = {
        'Host': 'wabi-us-gov-virginia-api.analysis.usgovcloudapi.net',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:103.0) Gecko/20100101 Firefox/103.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https',
        'ActivityId': 'e563af8e-0f7a-8787-1ca0-58fe2079e4df',
        'RequestId': '9da7e5e6-df12-f54a-89d2-777b88b76d12',
        'X-PowerBI-ResourceKey': '506d908d-d582-4c28-9fc4-963c67b0596b',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'https',
        'DNT': '1',
        'Connection': 'keep-alive'
    }


    body = '{"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"m","Entity":"Monkeypox Data","Type":0}],"Select":[{"Column":{"Expression":{"SourceRef":{"Source":"m"}},"Property":"Event Date"},"Name":"Monkeypox Data.Event Date"},{"Measure":{"Expression":{"SourceRef":{"Source":"m"}},"Property":"Count of UID running total in Event Date"},"Name":"Monkeypox Data.Count of UID running total in Event Date"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"m"}},"Property":"UID"}},"Function":2},"Name":"CountNonNull(Monkeypox Data.UID)"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"m"}},"Property":"Source"}}],"Values":[[{"Literal":{"Value":"\'HC\'"}}],[{"Literal":{"Value":"\'HOU\'"}}]]}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0,1,2]}]},"DataReduction":{"DataVolume":4,"Primary":{"Sample":{}}},"Version":1},"ExecutionMetricsKind":1}}]},"CacheKey":"{\\"Commands\\":[{\\"SemanticQueryDataShapeCommand\\":{\\"Query\\":{\\"Version\\":2,\\"From\\":[{\\"Name\\":\\"m\\",\\"Entity\\":\\"Monkeypox Data\\",\\"Type\\":0}],\\"Select\\":[{\\"Column\\":{\\"Expression\\":{\\"SourceRef\\":{\\"Source\\":\\"m\\"}},\\"Property\\":\\"Event Date\\"},\\"Name\\":\\"Monkeypox Data.Event Date\\"},{\\"Measure\\":{\\"Expression\\":{\\"SourceRef\\":{\\"Source\\":\\"m\\"}},\\"Property\\":\\"Count of UID running total in Event Date\\"},\\"Name\\":\\"Monkeypox Data.Count of UID running total in Event Date\\"},{\\"Aggregation\\":{\\"Expression\\":{\\"Column\\":{\\"Expression\\":{\\"SourceRef\\":{\\"Source\\":\\"m\\"}},\\"Property\\":\\"UID\\"}},\\"Function\\":2},\\"Name\\":\\"CountNonNull(Monkeypox Data.UID)\\"}],\\"Where\\":[{\\"Condition\\":{\\"In\\":{\\"Expressions\\":[{\\"Column\\":{\\"Expression\\":{\\"SourceRef\\":{\\"Source\\":\\"m\\"}},\\"Property\\":\\"Source\\"}}],\\"Values\\":[[{\\"Literal\\":{\\"Value\\":\\"\'HC\'\\"}}],[{\\"Literal\\":{\\"Value\\":\\"\'HOU\'\\"}}]]}}}]},\\"Binding\\":{\\"Primary\\":{\\"Groupings\\":[{\\"Projections\\":[0,1,2]}]},\\"DataReduction\\":{\\"DataVolume\\":4,\\"Primary\\":{\\"Sample\\":{}}},\\"Version\\":1},\\"ExecutionMetricsKind\\":1}}]}","QueryId":"","ApplicationContext":{"DatasetId":"d8982ae4-8df7-4ef9-9052-66e6e7ce0547","Sources":[{"ReportId":"8aa09953-0b4a-4907-b03a-1369ebafc6c5","VisualId":"671b76b48b259107b327"}]}}],"cancelQueries":[],"modelId":617686}'

    # We use the previous three variables to do a post request to powerbi
    r = requests.post(url, headers=headers, data=body)

    # We use the json() function to convert the response to a dictionary, then we navigate to the data we want
    r_json = r.json()['results'][0]['result']['data']['dsr']['DS'][0]['PH'][0]['DM0']

    # A function that converts epoch time to a readable date
    def epoch_to_date(epoch):
        return pd.to_datetime(epoch, unit='ms')

    # Empty dict to store the data
    data_dict = {}

    # Loop through r_json and add to data_dict.
    for i in r_json[1:]:
        date = i.get('C')[0]
        case_count = i.get('C')[1]
        data_dict[date] = case_count

    # Load data_dict into a pandas dataframe
    df = pd.DataFrame(data_dict.items(), columns=['date', 'case_count'])

    # Here we convert the date column to a datetime object
    df['date'] = df['date'].apply(epoch_to_date)

    # Find the number of new cases per day
    df['New cases'] = df['case_count'].diff()
    df['New cases'] = df['New cases'].fillna(0)
    df['New cases'] = df['New cases'].astype(int)

    # Find the average number of new cases per day
    df['7-day average'] = round(df['New cases'].rolling(7).mean(), 1)
    df['7-day average'] = df['7-day average'].fillna(0)

    # Export this data.
    df.to_csv('data/harris_county_historic.csv', index=False)

    # Get the last value in the case_count column
    last_case_count = df['case_count'].iloc[-1]
    new_cases = df['New cases'].iloc[-1]

    table_df = pd.DataFrame({
        '': ['Harris County'],
        'All time': [last_case_count],
        'New': ['+' + str(new_cases)]
    })

    table_df.to_csv('data/harris_table.csv', index=False)


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
getHarrisCases()
getTexasAgeData()
getTexasSexData()
getTexasSevenDayAverages()
createMetadata()
