from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime
import time
import csv

# Connect to Website
url = 'https://www.ecb.europa.eu/home/html/index.en.html'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
tables = soup.find_all('table', class_="stats-table")

# Select the desired table from the list
exchange_rates_table = [el.text.strip() for el in tables[1]]

# Convert date to date format
last_update_exch_rate_table = soup.find_all(class_="stats-table-footnote")[1].text.split(': ')[-1]
date_object = datetime.strptime(last_update_exch_rate_table, "%d %B %Y").date()

# Create DataFrame Currency exchange rates
headers = ['currency', 'rate', 'date']
df = pd.DataFrame(columns=headers)
for row in exchange_rates_table:
    if row:
        row = row.split('\n')
        exchange_rate_data = [row[0], row[-1], date_object]
        length = len(df)
        df.loc[length] = exchange_rate_data
print(df)
        

# Create CSV and write headers into the file
with open(r'C:\Users\Anastasia\projects\DataAnalysis\Web scraping\ECBR_currency_exhchange_rates.csv', 'w',
          newline='', encoding='UTF8') as f:
    writer = csv.writer(f)
    writer.writerow(headers)


# Combine all of the above code into one function and save to CSV file
def check_ecb_currency_rates():
    url = 'https://www.ecb.europa.eu/home/html/index.en.html'
    response= requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        tables = soup.find_all('table', class_="stats-table")
        exchange_rates_table = [el.text.strip() for el in tables[1]]
        last_update_exch_rate_table = soup.find_all(class_="stats-table-footnote")[1].text.split(': ')[-1]
        date_object = datetime.strptime(last_update_exch_rate_table, "%d %B %Y").date()

        for row in exchange_rates_table:
            if row:
                row =row.split('\n')
                exchange_rate_data = [row[0], row[-1], date_object]
                with open(r'C:\Users\Anastasia\projects\DataAnalysis\Web scraping\ECBR_currency_exhchange_rates.csv', 'a+', newline='', encoding='UTF8') as f:
                    writer = csv.writer(f)
                    writer.writerow(exchange_rate_data)
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
    

# add information about rates cumulatively once a day and save to CSV file
while(True):
    check_ecb_currency_rates()
    time.sleep(86400)

