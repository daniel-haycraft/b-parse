import requests


class ProApiClient:
	API_KEY = 'SQYRMMKXBRNKYPXDFE'

	@staticmethod
	def execute_post(url, params):
		"""Helper method to execute HTTP POST requests."""
		response = requests.post(url, data=params)
		return response.text

	@staticmethod
	def lookup_companies(company_name, city, postal_abbreviation):
		"""
		LCSBN Endpoint - LookupCompanies() function looks up Companies.
		[company_name] is required and must be at least 5 characters in length. (Example = Investment)
		[city] is optional, however if provided it should be a valid city name in the state or province you designate in postal_abbreviation. (Example = Los Angeles)
		[postal_abbreviation] is optional, however if provided it must be a valid Postal Abbreviation (i.e., CA, DE, FL, TX, ON, QC) in either the United States or Canada.
		Example API Call: LookupCompanies("Invest", "Los Angeles", "CA")
		Returns CompanyList Object
		"""
		params = {
			'k': ProApiClient.API_KEY,
			'ep': 'LCSBN',
			'n': company_name,
			'c': city,
			'pa': postal_abbreviation
		}
		return ProApiClient.execute_post('https://www.bizapedia.com/bdmservice-rest.aspx', params)

	@staticmethod
	def lookup_people(first_name, last_name, city, postal_abbreviation):
		"""
		LP Endpoint - The LookupPeople() function looks up Companies and their Principals.
		[first_name] is required and must be at least 2 characters in length. (Example = Jane)
		[last_name] is required and must be at least 2 characters in length. (Example = Doe)
		[city] is optional, however if provided it should be a valid city name in the state or province you designate in postal_abbreviation.
		[postal_abbreviation] is optional, however if provided it must be a valid Postal Abbreviation (i.e., CA, DE, FL, TX, ON, QC) in either the United States or Canada.
		Example API Call: LookupPeople("John", "Jones", "Los Angeles", "CA")
		Returns CompanyPrincipalList Object
		"""
		params = {
			'k': ProApiClient.API_KEY,
			'ep': 'LP',
			'fnm': first_name,
			'lnm': last_name,
			'c': city,
			'pa': postal_abbreviation
		}
		return ProApiClient.execute_post('https://www.bizapedia.com/bdmservice-rest.aspx', params)

	@staticmethod
	def lookup_addresses(address_street, city, postal_abbreviation, postal_code):
		"""
		LA Endpoint - The LookupAddresses() function looks up Addresses associated with Companies, Principals, and Trademarks.
		[address_street] is required and must be at least 3 characters in length. (example = 5750 Wilshire Blvd)
		[city] is required and must be at least 3 characters in length. (example = Los Angeles) 
		[postal_abbreviation] is optional, however if provided it must be a valid Postal Abbreviation (i.e., CA, DE, FL, TX, ON, QC) in either the United States or Canada. 
		[postal_code] is optional, however if provided it must be a valid Postal Code (i.e., 10001, 43215, 90401, M2K 1W9, M4L 1V2) in either the United States or Canada. 
		Example API Call: LookupAddresses("5750 Wilshire Blvd", "Los Angeles", "CA", "90036")
		Returns AddressLists Object
		"""
		params = {
			'k': ProApiClient.API_KEY,
			'ep': 'LA',
			'a': address_street,
			'c': city,
			'pa': postal_abbreviation,
			'pc': postal_code
		}
		return ProApiClient.execute_post('https://www.bizapedia.com/bdmservice-rest.aspx', params)

	@staticmethod
	def lookup_trademarks(mark_identification, owner_name):
		"""
		LT Endpoint - The LookupTrademarks() function looks up Trademarks registered with the USPTO by Mark Identification and/or Owner Name.
		Either [mark_identification] or [owner_name] is required and you may provide both.
		[mark_identification] is optional, however if provided it must be at least 2 characters in length. (example = Widget) 
		[owner_name] is optional, however if provided it must be at least 2 characters in length. (example = Acme, LLC) 
		Example API Call: LookupTrademarks("License", "Utah State Bar")
		Returns TrademarkList Object
		"""
		params = {
			'k': ProApiClient.API_KEY,
			'ep': 'LT',
			'tm': mark_identification,
			'tmo': owner_name
		}
		return ProApiClient.execute_post('https://www.bizapedia.com/bdmservice-rest.aspx', params)

	@staticmethod
	def lookup_company_by_file_number(postal_abbreviation, file_number):
		"""
		LCBFN Endpoint - The LookupCompanyByFileNumber() function looks up a single Company by its filing state and state issued file number.
		[postal_abbreviation] is required and must be a valid Postal Abbreviation (i.e., CA, DE, FL, TX, ON, QC) in either the United States or Canada.
		[file_number] is required and must be a valid state issued file number. (Example = L22000999999)
		Example API Call: LookupCompanyByFileNumber("CA", "806592")
		Returns Company Object
		"""
		params = {
			'k': ProApiClient.API_KEY,
			'ep': 'LCBFN',
			'pa': postal_abbreviation,
			'fn': file_number
		}
		return ProApiClient.execute_post('https://www.bizapedia.com/bdmservice-rest.aspx', params)

	@staticmethod
	def get_api_call_count():
		"""
		GACC Endpoint - The GetApiCallCount() function returns the number of live API calls you've made since your last renewal.
		Example API Call: GetApiCallCount()
		Returns Integer
		"""
		params = {
			'k': ProApiClient.API_KEY,
			'ep': 'GACC'
		}
		return ProApiClient.execute_post('https://www.bizapedia.com/bdmservice-rest.aspx', params)



