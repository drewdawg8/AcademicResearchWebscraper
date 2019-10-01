import urllib.request
import xlsxwriter
from bs4 import BeautifulSoup

valid_years = ['2011','2012','2013','2014']
donation_master_list = []


def retrieve_donations(row):
	''' retrieves donations and the year'''
	link = str(row.find('a'))
	start_index = link.index('/')
	end_index = link.index('>')
	#link to get full donation total in year range
	link = 'https://www.vpap.org' + link[start_index:end_index-1]
	print(link)
	donation_page = urllib.request.urlopen(link)
	donation_soup = BeautifulSoup(donation_page, 'html.parser')
	table = donation_soup.find('table')
	table_body = table.find('tbody')
	table_rows = table_body.find_all('tr')
	donations = {}
	for row in table_rows:
		text = row.get_text().replace('\n','')
		text = text.lstrip(' ')
		amount = text[:text.index(' ')]
		text = text[text.index(' '):].lstrip(' ')
		date = text[::-1].lstrip(' ')[:4]
		date = date[::-1]
		donations[text.replace(' ', '')] = amount
		
		
		return donations

def retrieve_donation_info(row, donor):
	''' compiles donation information to create donation objects to put into masterlist'''
	donation_info = row.get_text().replace('\n', '')
	end_index = donation_info.index(' ') # end of donation amount
	campaign = donation_info[end_index:].lstrip(' ') # strip out donation amount
	print(campaign)
	if '-' not in campaign:
		full_name = campaign
	else:
		first_name = campaign[campaign.index('-')+2:].rstrip(' ') #first name with extraneous spaces stripped 
		last_name = campaign[:campaign.index(' ')]
		full_name = first_name + ' ' + last_name
	donations = retrieve_donations(row)
	for date in donations:
			donation = Donation(full_name, donations[date], date, donor)
			donation_master_list.append(donation)
			print(donation)

def generate_url(donor):

	url = 'https://www.vpap.org/search/?q='
	donor = donor.replace(' ', '+')
	url += donor + '&facet=donors'
	return url

def get_donors(search_term):

	start_page = generate_url(search_term)
	print(start_page)
	#REQUEST PAGE
	page = urllib.request.urlopen(start_page)
	# SOUP IT
	soup = BeautifulSoup(page, 'html.parser')


	# FIND THE SEARCH RESULTS
	search_results = soup.find_all('a', attrs={'class': 'list-group-item'})
	element = None
	# Find link for donor page
	for result in search_results:
		#Make sure the search result is correct and it is a donor
		if search_term in result.get_text() and 'donors' in str(result):
			element = str(result)


	# Pull the href link from the element
	if element == None:
		return
	start_index = element.index('/')
	end_index = element.index('>')
	href = element[start_index:end_index - 1]

	donor_page = "https://www.vpap.org" + href +'?start_year=2011&end_year=2014'
	print(donor_page)
	donor_page_2 = urllib.request.urlopen(donor_page)
	donor_soup = BeautifulSoup(donor_page_2, 'html.parser')
	# PULL RELEVENT INFO
	donations_dict = {}
	table = donor_soup.find('table')
	table_body = table.find('tbody')
	table_rows = table_body.find_all('tr')
	#WILL NEED TO ITERATE THROUGH TABLE
	for row in table_rows:
		retrieve_donation_info(row,donor)


'''

Donation class to help with possible manipulation and debugging later on

'''

class Donation:

	def __init__(self, name, amount, year, donor):
		self.name = name
		self.amount = amount
		self.year = year
		self.donor = donor

	def __str__(self):
		return self.name + ' recieved ' + self.amount + ' from ' + self.donor + ' in ' + self.year + '.'


# AUTOMATE THIS LATER
file = open('donors.txt','r')
donors = file.readline()
donors = donors.split(', ')
for donor in donors:
	get_donors(donor)
#put into spreadsheet
workbook = xlsxwriter.Workbook('data.xlsx')
worksheet = workbook.add_worksheet()
worksheet.write('A1', 'Donor')
worksheet.write('B1', 'Recipient')
worksheet.write('C1', 'Date')
worksheet.write('D1', 'Amount')
ctr = 2
for donation in donation_master_list:
	worksheet.write('A' + str(ctr), donation.donor)
	worksheet.write('B' + str(ctr), donation.name)
	worksheet.write('C' + str(ctr), donation.year)
	worksheet.write('D' + str(ctr), donation.amount)
	ctr+=1

workbook.close()





	



