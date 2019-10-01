import urllib.request
import xlsxwriter
from bs4 import BeautifulSoup
donation_list = []
class Donation:

	def __init__(self, donor, recipient, amount,date):
		self.donor = donor
		self.recipient = recipient
		self.amount = amount
		self.date = date

	def __str__(self):
		return self.recipient + " recieved " + self.amount + " from " + self.donor + " on " + self.date + "."


def import_list():
	file = open('donors.txt','r')
	donors = file.readlines()
	donors = [d.replace('\n','') for d in donors]
	donors = [d.replace('-','') for d in donors]
	donors = [d.replace('.','') for d in donors]
	return donors

def generate_search_url(donor):
	'''
	Generates the search url
	'''
	url = 'https://www.vpap.org/search/?q='
	donor = donor.replace(' ', '+')
	url += donor + '&facet=donors'
	return url

def format_donor(string):
	string = string.replace(' ', '-')
	return string

def generate_recipients_link(string, donor):
	string = str(string)
	start_index = string.index('/')
	end_index = string.index('>')
	href = string[start_index:end_index - 1]
	donor = format_donor(donor)
	link = "https://www.vpap.org" + href + '-' + donor + '/?start_year=2011&end_year=2014'
	return link

def grab_campaign(row):
	donation_info = row.get_text().replace('\n', '')
	donation_info = donation_info[donation_info.index(' '):].lstrip(' ')
	return donation_info

def make_soup(link):
	'''
	Creates a soup object
	'''
	page = urllib.request.urlopen(link)
	soup = BeautifulSoup(page, 'html.parser')
	return soup

def grab_donations(row):
	href = str(row.find('a'))
	start_index = href.index('"')
	end_index = href.index('>')
	href = href[start_index+1:end_index - 1]
	full_link = 'https://www.vpap.org' + href
	#print(full_link)
	final_soup = make_soup(full_link)
	table = final_soup.find('table', attrs = {'class' : 'table table-striped'})
	table_body = table.find('tbody')
	table_rows = table_body.find_all('tr')
	donations_dict = {}
	for row in table_rows:
		text = row.get_text().replace('\n', '').lstrip(' ')
		index = text.index(' ')
		amount = text[:index]
		text = text[index:].lstrip(' ').rstrip(' ')
		date = text
		if 'Details' in date:
			date = date.replace('Details', '').rstrip(' ')
		donations_dict[date] = amount
	return donations_dict

def scrape_donations(soup, donor):
	#Actual data scraping done here
	table = soup.find('table')
	if table == None:
		return
	table_body = table.find('tbody')
	table_rows = table_body.find_all('tr')
	for row in table_rows:
		campaign = grab_campaign(row).rstrip(' ')
		#Stored as {year:amount}
		donations_dict = grab_donations(row)
		#create donation objects
		for date in donations_dict:
			donation = Donation(donor, campaign, donations_dict[date], date)
			donation_list.append(donation)

def scrape_data(donor):
	search_page = generate_search_url(donor)

	search_soup = make_soup(search_page)
	results = search_soup.find_all('a', attrs = {'class': 'list-group-item'})

	for result in results:
		donor_page = generate_recipients_link(result, donor)
		donor_soup = make_soup(donor_page)
		scrape_donations(donor_soup, donor)

def generate_spreadsheet():
	workbook = xlsxwriter.Workbook('raw_data.xlsx')
	worksheet = workbook.add_worksheet()
	worksheet.write('A1', 'Donor')
	worksheet.write('B1', 'Recipient')
	worksheet.write('C1', 'Date')
	worksheet.write('D1', 'Amount')
	ctr = 2
	for donation in donation_list:
		worksheet.write('A' + str(ctr), donation.donor)
		worksheet.write('B' + str(ctr), donation.recipient)
		worksheet.write('C' + str(ctr), donation.date)
		worksheet.write('D' + str(ctr), donation.amount)
		ctr+=1

	workbook.close()

donors = import_list()
for donor in donors:
	scrape_data(donor)
generate_spreadsheet()