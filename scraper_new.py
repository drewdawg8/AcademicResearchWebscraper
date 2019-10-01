import urllib.request
import xlsxwriter
from bs4 import BeautifulSoup

test_donor = 'Georgia-Pacific Corp'
donation_list = []

class Donation:

	def __init__(self, donor, recipient, year, amount):
		self.year = str(year)
		self.amount = str(amount)
		self.donor = str(donor)
		self.recipient = str(recipient)

	def __str__(self):
		return self.recipient + " recieved " + self.amount + " from " + self.donor + " on " + self.year + "."

def generate_search_url(donor):
	'''
	Generates the search url
	'''
	url = 'https://www.vpap.org/search/?q='
	donor = donor.replace(' ', '+')
	url += donor + '&facet=donors'
	return url

def get_search_page(donor):
	''' 
	Gets the search results for the donor. 
	Needed to find the correct URL
	'''
	search_page = generate_search_url(donor)
	print(search_page)
	return search_page

def grab_href(string, donor):
	start_index = string.index('/')
	end_index = string.index('>')
	href = string[start_index:end_index - 1]
	donor = format_donor(donor)
	link = "https://www.vpap.org" + href + '-' + donor + '/?start_year=2011&end_year=2014'
	return link

def format_donor(string):
	string = string.replace(' ', '-')
	return string

def format_recipient(string): 
	#jank check to differentiate people from groups
	if 'for' in string and '-' in string:
		index = string.index(' ')
		string = string[index:].lstrip(' ')
		index = string.index(' ')
		last_name = string[:index]
		index = string.index('-')
		first_name = string[index+2:]
		recipient = first_name.replace(' ', '') + " " + last_name
	else:
		index = string.index(' ')
		string = string[index:]
		recipient = string.lstrip(' ').rstrip(' ')

	return recipient


def soup_page(link):
	'''
	Creates a soup object
	'''
	page = urllib.request.urlopen(link)
	soup = BeautifulSoup(page, 'html.parser')
	return soup

def grab_campaign(row):
	'''
	Grabs full name if htere is one or campaign otherwise
	'''
	donation_info = row.get_text().replace('\n', '')
	#print(donation_info)
	recipient = format_recipient(donation_info)
	return recipient

def grab_amt_year(row):
	href = str(row.find('a'))
	start_index = href.index('"')
	end_index = href.index('>')
	href = href[start_index+1:end_index - 1]
	full_link = 'https://www.vpap.org' + href
	#print(full_link)
	final_soup = soup_page(full_link)
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
		campaign = grab_campaign(row)
		#Stored as {year:amount}
		donations_dict = grab_amt_year(row)
		#create donation objects
		for date in donations_dict:
			donation = Donation(donor, campaign, date, donations_dict[date])
			donation_list.append(donation)
			#print(donation)

def scrape(donor):
	search_page = get_search_page(donor)
	search_soup = soup_page(search_page)
	#Search by class list-group-item to find the link for the search result
	results = search_soup.find_all('a', attrs = {'class': 'list-group-item'})
	element = None
	for result in results:
		if donor.lower() in result.get_text().lower().replace('-', ''):
			element = str(result)
	
	#Empty search
	if element == None:
		return 
	donor_page = grab_href(element,donor)
	donor_soup = soup_page(donor_page)

	#Scrape donations
	scrape_donations(donor_soup, donor)


file = open('donors.txt','r')
donors = file.readlines()
for donor in donors:
	scrape(donor.replace('\n',''))

workbook = xlsxwriter.Workbook('data.xlsx')
worksheet = workbook.add_worksheet()
worksheet.write('A1', 'Donor')
worksheet.write('B1', 'Recipient')
worksheet.write('C1', 'Date')
worksheet.write('D1', 'Amount')
ctr = 2
for donation in donation_list:
	worksheet.write('A' + str(ctr), donation.donor)
	worksheet.write('B' + str(ctr), donation.recipient)
	worksheet.write('C' + str(ctr), donation.year)
	worksheet.write('D' + str(ctr), donation.amount)
	ctr+=1

workbook.close()