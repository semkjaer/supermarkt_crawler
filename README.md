# supermarkt_crawler
install python 3.X     
make&activate venv    
cd supermarktcrawler   
pip install -r requirements.txt   
'scrapy crawl albert_heijn -o albert_heijn.jl -t jl' om de scraper te runnen   
IS_DEV in supermarktcrawler/settings.py limiteerd items gescraped tot 10 wanneer 
True, wanneer False crawled ie de hele site   
albert_heijn.py regel 20-23 selecteerd ie je chromedriver voor selenium, path kan anders zijn op verschillende PCs
