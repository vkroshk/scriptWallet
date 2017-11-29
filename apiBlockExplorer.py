import sys
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode

BASE_URL = 'https://blockexplorer.com'
TIMEOUT = 30


def call_api(resource):
    try:
        req = Request(BASE_URL + resource, headers={'User-Agent': 'Mozilla/5.0'})
        response = urlopen(req, timeout=TIMEOUT).read()
        return response.decode('utf-8')
    
    except HTTPError as e:
    	the_str = e.read().decode('utf-8')
    	error = []
    	for key, value in json.loads(the_str).items():
    		error.append('\n\t{}: {}'.format(str(key), str(value)))
    	print ('К сожалению, возникла ошибка: {}\n'.format(''.join(error)))
    	sys.exit()


def process_url(fn):
	def wrapper(wallet):
		return json.loads(call_api(fn(wallet).format(wallet)))
	return wrapper


class ApiBlockExplorer(object):

	@staticmethod
	@process_url
	def validate_address(wallet):
		return '/api/addr-validate/{}'

	@staticmethod
	@process_url
	def get_balance(wallet):
		return '/api/addr/{}/balance'

	@staticmethod
	@process_url
	def all_transaction(wallet):
		return '/api/txs/?address={}'

	@staticmethod
	def inc_transactions(wallet):
		 transactions = ApiBlockExplorer.process_transactions(wallet)
		 return transactions['inc_trns']

	@staticmethod
	def out_transactions(wallet):
		 transactions = ApiBlockExplorer.process_transactions(wallet)
		 return transactions['out_trns']

	@staticmethod
	def process_transactions(wallet):
		trns = {}
		trns['inc_trns'] = {}
		trns['out_trns'] = {}
		transactions = ApiBlockExplorer.all_transaction(wallet)['txs']
		for trn in transactions:
			
			inc_trns = []
			for inc_t in trn['vin']:
				inc_trn = {}
				inc_trn['address'] = inc_t['addr']
				inc_trn['value'] = inc_t['value']
				inc_trn['time'] = trn['time']
				inc_trns.append(inc_trn)
			trns['inc_trns'][trn['txid']] = inc_trns


			out_trns = []
			for out_t in trn['vout']:
				out_trn = {}
				out_trn['address'] = out_t['scriptPubKey']['addresses'][0]
				out_trn['value'] = out_t['value']
				out_trn['time'] = trn['time']
				out_trns.append(out_trn)
			trns['out_trns'][trn['txid']] = out_trns

		return trns
