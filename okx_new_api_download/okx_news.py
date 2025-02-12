import argparse
import os
import sys

import requests
from datetime import datetime, timedelta

# Define the URL
URL = "http://www.okx.com/api/v5/support/announcements"
URL_ANNTYPES = "http://www.okx.com/api/v5/support/announcement-types"

# Define parameters for search
# START_DATE = '2024-12-01'
# END_DATE = '2024-12-05'
# FOLDER = f'./okx_news_folder/'


def get_anntypes(url_anntypes: str) -> list:
    """get all existing types of announcements from
    url: https://www.okx.com/docs-v5/en/?python#announcement-get-announcement-types"""
    response = requests.get(url_anntypes)
    ann_types = []
    if response.status_code == 200:
        try:
            ann_types_data = response.json()['data']
            for data in ann_types_data:
                ann_types.append(data['annType'])
        except Exception as exception:
            print(f"No information about announcement types, exception: {exception}.")
    else:
        print(f"Failed to retrieve data from url {URL_ANNTYPES}, response code: {response.status_code}.")
        sys.exit(1)  # exit if you can't retrieve data from URL_ANNTYPES

    return ann_types


def convert_timestamp_from_ms_to_s(timestamp_ms: str) -> int:
    """Convert timestamp from ms to seconds"""
    return int(int(timestamp_ms) / 1000)


def get_start_date_timestamp(start_date: str) -> int:
    """Redefine start_date to get timestamp at the beginning of the day"""
    return int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())


def get_end_date_timestamp(end_date: str) -> int:
    """Redefine end_date to get timestamp at the end of the day: next day in timestamp minus 1 sec to get 23:59:59"""
    return int((datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)).timestamp()) - 1


def convert_timestamp_ms_to_date_str(timestamp_ms: str) -> str:
    """Convert Unix timestamp format in milliseconds into date str format"""
    return datetime.fromtimestamp(int(timestamp_ms) / 1000).strftime("%Y-%m-%d")


def check_date_interval(timestamp_ms: str, start_date: str, end_date: str) -> bool:
    """Check that new's date is in required date interval"""
    start_date_timestamp = get_start_date_timestamp(start_date)
    end_date_timestamp = get_end_date_timestamp(end_date)
    return start_date_timestamp <= convert_timestamp_from_ms_to_s(timestamp_ms) <= end_date_timestamp


def check_dates(start_date: str, end_date: str) -> bool:
    """Check that date format is string in format "2024-12-31 and start_date less or equal end_date"""
    date_format = "%Y-%m-%d"

    try:
        # Check if the dates are in the correct format
        start = datetime.strptime(start_date, date_format)
        end = datetime.strptime(end_date, date_format)

        # Check if start_date is less than or equal to end_date
        if start <= end:
            return True
        else:
            print("Error: start_date must be less than or equal to end_date.")
            return False
    except ValueError:
        print("Error: Dates must be in the format YYYY-MM-DD.")
        return False


def dump_okx_news(start_date: str, end_date: str, folder='./okx_news_folder/', anntype=None, use_subfolders=False):
    """Dump news within specified date interval to the folder by different dates (sub_folders are optional),
    it's possible to specify annType to get one news category"""

    if not check_dates(start_date, end_date):
        exit(1)                    # exit if dates in the wrong format

    # define number of pages for the loop
    if anntype is not None and anntype in get_anntypes(URL_ANNTYPES):
        response = requests.get(URL, params={"annType": anntype})
    else:
        response = requests.get(URL)

    if response.status_code == 200:
        try:
            num_pages = int(response.json()['data'][0]['totalPage'])
        except Exception as exception:
            num_pages = 1
            print(f"No information about total number of pages, exception: {exception}.")
    else:
        print(f"Failed to retrieve data from url {URL}, response code: {response.status_code}.")
        sys.exit(1)                             # exit if you can't retrieve data from URL

    page = 1
    count_news = 0

    while page <= num_pages:
        if anntype is not None:
            params = {"annType": anntype, "page": page}
        else:
            params = {"page": page}

        response_page = requests.get(URL, params=params)
        news_on_page = response_page.json()['data'][0]['details']   # get all news in the list from page
        # get time of the latest news on the page and compare with the start date to continue searching news or not
        time_of_latest_news_on_page = response_page.json()['data'][0]['details'][0]['pTime']

        if convert_timestamp_from_ms_to_s(time_of_latest_news_on_page) > get_start_date_timestamp(start_date) \
                and news_on_page:
            for item in news_on_page:

                if check_date_interval(item['pTime'], start_date, end_date):
                    response = requests.get(f"{item['url']}")
                    if response.status_code == 200:
                        try:
                            file_title = item['title'].replace("[\\*/\\\\!\\|:?<>]", " ").replace('/', ' ')

                            if use_subfolders:
                                folder_name = convert_timestamp_ms_to_date_str(item['pTime'])
                                folder_path = os.path.join(folder, folder_name)
                            else:
                                folder_path = folder

                            # Check if the folder already exists
                            if not os.path.exists(folder_path):
                                os.makedirs(folder_path)
                                print(f"Created folder: {folder_path}.")
                            else:
                                print(f"Folder already exists: {folder_path}.")

                            with open(f"{folder_path}/{item['pTime']}_{file_title}.html",
                                      "w", encoding='UTF-8') as outfile:
                                outfile.write(response.text)
                                print(f"{item['pTime']}_{file_title} saved to the {folder_path}")
                                count_news += 1
                        except Exception as exception:
                            print(f"No title for the news {exception}.")
                    else:
                        print(f"Failed to retrieve data from url {item['url']}, response code: {response.status_code}.")
            page += 1
        else:
            break

    print(f"Loading complete: {count_news} news downloaded")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download okx news')
    parser.add_argument('--start_date', type=str,
                        help='example "2024-12-01"', required=True)
    parser.add_argument('--end_date', type=str,
                        help='example "2024-12-01"', required=True)
    parser.add_argument('--folder', type=str,
                        help='path to download news', default='./okx_news_folder/')
    parser.add_argument('--anntype', type=str,
                        help='news type, e.g. "announcements-delistings"', default=None)
    parser.add_argument("--use_subfolders", help="increase output verbosity",
                        action="store_true")
    args = parser.parse_args()
    dump_okx_news(args.start_date, args.end_date, args.folder, args.anntype, args.use_subfolders)
