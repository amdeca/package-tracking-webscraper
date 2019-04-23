# azulcargo-webscraper
Webscraper for the Azul cargo tracking website

Track shipments on the http://www.azulcargo.com.br//Rastreio.aspx website quickly.

## Installation
This scraper requires selenium, beautifulSoup and PhantomJS.
Selenium and beautifulSoup can be installed with
```bash
pip install selenium
pip install beautifulSoup
```
PhantomJS is a headless webdriver that cannot be installed via pip. More info on:

Windows install: https://www.joecolantonio.com/how-to-install-phantomjs/

Ubuntu install: https://www.vultr.com/docs/how-to-install-phantomjs-on-ubuntu-16-04

## Usage
Run the azulscraper.py script with
```bash
python azulscraper.py
```
and paste the document numbers you wish to track and they will be exported to a .csv file.

Alternatively, you can use the scrape method of the AzulcargoScraper class, passing in a list of documents to be scraped and the output file name:
```python
import AzulcargoScraper

scraper = AzulcargoScraper()
scraper.scrape(input_list=list_of_documents , file='scraping_output.csv')
```
