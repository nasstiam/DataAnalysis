OKX News downloader


description:
okx_news download news from the OKX crypro exchange https://www.okx.com/help/category/announcements


You can specify the following parameters:
start_date - expected in string format "2024-12-31" 
end_date - expected in string format "2024-12-31", start_date should be less or equal the end_date
folder - folder to save the news
sub_folders - by default (False) all news downloaded into one folder, if True news downloaded into folders by date
anntype - announcement-types - you can specify news type that you download, None by default - for all news

anntype from https://www.okx.com/docs-v5/en/?python#announcement-get-announcement-types:
- announcements-new-listings
- announcements-delistings
- announcements-trading-updates
- announcements-deposit-withdrawal-suspension-resumption
- announcements-p2p-trading
- announcements-web3
- announcements-earn
- announcements-jumpstart
- announcements-api
- announcements-okb-buy-back-burn
- announcements-others


Installation instructions:
Create and activate a virtual environment:
python3 -m venv venv

If you have Linux/mac OS
source venv/bin/activate

If you have windows
source venv/scripts/activate python -m pip install --upgrade pip

Install the dependencies from the file requirements.txt:
pip install -r requirements.txt


Examples to run script:
1) download OKX news "announcements-delistings" from "2024-12-01" to "2024-12-05" using subfolders by date
python okx_news.py --start_date "2024-12-01" --end_date "2024-12-05" --folder './okx_news_folder/' --anntype 'announcements-delistings' --use_subfolders

2) download all OKX news from "2024-12-01" to "2024-12-05" in one folder './okx_all_news_folder/'
python okx_news.py --start_date "2024-12-01" --end_date "2024-12-05" --folder './okx_all_news_folder/' 

3) download all OKX news from "2024-12-01" to "2024-12-05" in one default folder 
python okx_news.py --start_date "2024-12-01" --end_date "2024-12-05" 