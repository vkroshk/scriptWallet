import unittest
from scriptWallet import CommandHandler
from apiBlockExplorer import ApiBlockExplorer
from unittest.mock import MagicMock, patch, Mock

class TestApiBlockExplorer(unittest.TestCase):

	def test_valid_address(self):
		cmd_hendler = CommandHandler({'b': True, 'i': False, 'o': False, 'f': False, 'wallet': ['19SokJG7fgk8iTjemJ2obfMj14FM16nqzj']})
		with patch.object(ApiBlockExplorer, 'validate_address', return_value=True) as mock_method:
			r = cmd_hendler.validate_wallet('19SokJG7fgk8iTjemJ2obfMj14FM16nqzj')
		self.assertEqual(r, True)

	def test_not_valid_address(self):
		cmd_hendler = CommandHandler({'b': True, 'i': False, 'o': False, 'f': False, 'wallet': ['19SokJG7fgk8iTjemJ2obfMj14FM16nqzj']})
		with patch.object(ApiBlockExplorer, 'validate_address', return_value=False) as mock_method:
			r = cmd_hendler.validate_wallet('19SokJG7fgk8iTjemJ2obfMj14FM16nqzj')
		self.assertEqual(r, False)

	def test_get_balance(self):
		cmd_hendler = CommandHandler({'b': True, 'i': False, 'o': False, 'f': False, 'wallet': ['19SokJG7fgk8iTjemJ2obfMj14FM16nqzj']})
		with patch.object(ApiBlockExplorer, 'get_balance', return_value=100500) as mock_method:
			r_str = cmd_hendler.get_balance('19SokJG7fgk8iTjemJ2obfMj14FM16nqzj')
		self.assertEqual(r_str, '\tБаланс - 0.001005')

	def test_get_inc_trns(self):
		cmd_hendler = CommandHandler({'b': False, 'i': True, 'o': False, 'f': False, 'wallet': ['19SokJG7fgk8iTjemJ2obfMj14FM16nqzj']})
		data = {
			"b3ee69be6c92c633df196d5cfd5ebbb812d83d9ecd7274905da5135777f7ac18": [{
				'address': '1PTFmHJLfzpjMbeVti39XCAhJVugCrhkjB',
				'value': 0.01375441,
				'time': 1511897801
			}]
		}
		with patch.object(ApiBlockExplorer, 'inc_transactions', return_value=data) as mock_method:
			r_str = cmd_hendler.get_inc_trns('19SokJG7fgk8iTjemJ2obfMj14FM16nqzj')
		self.assertEqual(r_str, '\tВсе входящие транзакции - \n\t\tДата: 2017-11-28\n\t\tАдресс: 1PTFmHJLfzpjMbeVti39XCAhJVugCrhkjB\n\t\tBTC: 0.01375441\n')

	def test_get_out_trns(self):
		cmd_hendler = CommandHandler({'b': False, 'i': True, 'o': False, 'f': False, 'wallet': ['19SokJG7fgk8iTjemJ2obfMj14FM16nqzj']})
		data = {
			"b3ee69be6c92c633df196d5cfd5ebbb812d83d9ecd7274905da5135777f7ac18": [{
				'address': '1PTFmHJLfzpjMbeVti39XCAhJVugCrhkjB',
				'value': 0.01375441,
				'time': 1511897801
			}]
		}
		with patch.object(ApiBlockExplorer, 'out_transactions', return_value=data) as mock_method:
			r_str = cmd_hendler.get_out_trns('19SokJG7fgk8iTjemJ2obfMj14FM16nqzj')
		self.assertEqual(r_str, '\tВсе исходящии транзакции - \n\t\tДата: 2017-11-28\n\t\tАдресс: 1PTFmHJLfzpjMbeVti39XCAhJVugCrhkjB\n\t\tBTC: 0.01375441\n')

	def test_save_format_str(self):
		cmd_hendler = CommandHandler({'b': False, 'i': True, 'o': False, 'f': False, 'wallet': ['19SokJG7fgk8iTjemJ2obfMj14FM16nqzj']})
		cmd_hendler.format_str = '\t\tЭто не тот адресс: {a} который ты ищешь\n'
		data = {
			"b3ee69be6c92c633df196d5cfd5ebbb812d83d9ecd7274905da5135777f7ac18": [{
				'address': '1PTFmHJLfzpjMbeVti39XCAhJVugCrhkjB',
				'value': 0.01375441,
				'time': 1511897801
			}]
		}
		with patch.object(ApiBlockExplorer, 'out_transactions', return_value=data) as mock_method:
			r_str = cmd_hendler.get_out_trns('19SokJG7fgk8iTjemJ2obfMj14FM16nqzj')
		self.assertEqual(r_str, '\tВсе исходящии транзакции - \n\t\tЭто не тот адресс: 1PTFmHJLfzpjMbeVti39XCAhJVugCrhkjB который ты ищешь\n')

if __name__ == '__main__':
    unittest.main()