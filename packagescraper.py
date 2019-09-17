from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime
import csv
import os.path

class PackageScraper(object):
    def __init__(self):
        self.url = 'http://www.azulcargo.com.br//Rastreio.aspx'
        self.driver = webdriver.PhantomJS()
    
    def scrape(self, input_list=None , file='output.csv'):
        self.driver.get(self.url)

        #Fills the Javascript list
        for element in input_list:
            try:
                #print("Inserting: {}".format(element))
                self.driver.find_element_by_id('ctl00_cphBody_Inferior_txtNumero').send_keys(element)
                self.driver.find_element_by_id('ctl00_cphBody_Inferior_lkbAdicionar').click()
                sleep(1)
            except NoSuchElementException:
                sleep(4)
                self.driver.find_element_by_id('ctl00_cphBody_Inferior_txtNumero').send_keys(element)
                self.driver.find_element_by_id('ctl00_cphBody_Inferior_lkbAdicionar').click()
                sleep(3)
                
        sleep(3)
        print("Tracking ...")
        self.driver.find_element_by_id('ctl00_cphBody_Inferior_lkbRastrear').click()
        sleep((len(input_list)/2) * 1.5)
        
        #Start parsing
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        index = 0
        for container in soup.find_all('div', class_='panel panel-info')[2:]:
            document_data = []
            awb_number = input_list[index]
            header_list = container.find_all('div', class_='texto-medio')
            #Extract header information
            try:
                awb_number = header_list[1].text.strip()
                volumes = header_list[3].text.strip()
                weight = header_list[5].text.strip().replace(",",".")
                emit_date = header_list[7].text.strip()
                delivery_date = header_list[9].text.strip()
                #delivery_date will be empty if package has not arrived yet
                if delivery_date.isspace() == True:
                    delivery_date = 'N/A'
                origin = header_list[11].text.strip().replace(" ","").replace("\n","")
                destination = header_list[13].text.strip().replace(" ","").replace("\n","")
            except IndexError:
                volumes = 'Invalid'
                weight = 'Invalid'
                emit_date = 'Invalid'
                delivery_date = 'Invalid'
                origin = 'Invalid'
                destination = 'Invalid'

            try:    
                #Extract table information
                table = container.find('table')
                arrival_list = []
                ship_list = []
                for tr in table.find_all('tr')[1:]:
                    td = tr.find_all('td')
                    #Check 'Details' field
                    retention_date = 'N/A'
                    release_date = 'N/A'
                    arrival_date = 'N/A'
                    if 'Saída do voo' in td[1].text:
                        #ship_date = td[0].text
                        ship_list.append(td[0].text)
                    elif 'Chegada do voo' in td[1].text:
                        #Creates list with all cities with 'Flight Arrived' status                    
                        if td[3].text.strip()[:3] in destination:
                            arrival_list.append(td[0].text)
                        else:
                            arrival_date = 'N/A'  
                    elif 'NOTA FISCAL RETIDA' in td[1].text:
                        retention_date = td[0].text
                    elif 'NOTA FISCAL LIBERADA' in td[1].text:
                        release_date = td[0].text

                if arrival_list:
                    arrival_date = arrival_list[0]
                if ship_list:
                    ship_date = ship_list[-1]
                if not ship_list:
                    ship_date = 'N/A'

            except AttributeError:
                retention_date = 'Invalid'
                release_date = 'Invalid'
                arrival_date = 'Invalid'
                ship_date = 'Invalid'
                
            document_data = [
                awb_number, origin, destination, 
                volumes, weight, emit_date, 
                ship_date, arrival_date, retention_date, 
                release_date, delivery_date, str(datetime.now())[:-7]
            ]

            file_exists = os.path.isfile(file)
            with open(file, 'a', newline='') as csvFile:
                writer = csv.writer(csvFile)
                #check if file exists
                if not file_exists:
                    writer.writerow(['awb_number', 'origin', 'destination', 'volumes', 
                    'weight', 'emit_date', 'ship_date', 'arrival_date', 
                    'retention_date', 'release_date', 'delivery_date', 'timestamp'])
                #Write the rest o the data
                writer.writerow(document_data)
            csvFile.close()
            index += 1
        
        self.driver.quit()

def command_line_input():
    return str(input("\nType AWB document numbers : "))

#https://chrisalbon.com/python/data_wrangling/break_list_into_chunks_of_equal_size/
def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]

if __name__ == "__main__":
    scraper = PackageScraper()
    doclist = []
    user_input = ''
    while user_input != 'start':
        user_input = command_line_input()
        if user_input == 'start':
            print("Scraping {} documents".format(len(doclist)))
            #Removes duplicates
            doclist = list(dict.fromkeys(doclist))
            #website only supports 30 docs at once. If doclist > 30, divide in jobs
            if len(doclist) <= 30:
                scraper.scrape(input_list=doclist , file='output.csv')
                print("Finished")
            
            else:
                print("Number of documents exceeds 30. Splitting in parts")
                list_iter = list(chunks(doclist, 30))
                for split_list in list_iter:
                    scraper.scrape(input_list=split_list , file='output.csv')
                print("Finished")
        else:
            doclist.append(user_input)