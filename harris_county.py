import json

import pandas as pd
import requests


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

getHarrisCases()
