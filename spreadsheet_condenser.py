import xlsxwriter

class Donation:

	def __init__(self, donor, recipient, amount, year):
		self.donor = donor
		self.recipient = recipient
		self.amount = amount
		self.year = year


workbook = xlsxwriter.Workbook('raw_data.xlsx')
worksheet = workbook.get_worksheet_by_name('')
ctr = 1
for row in worksheet:
	print(worksheet['A'+str(ctr)].value)
	ctr+=1
workbook.close()
