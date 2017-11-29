# -*- coding: UTF-8 -*-
import sys
import signal
import argparse
import random
from apiBlockExplorer import ApiBlockExplorer
from datetime import datetime
from bitcoinlib.wallets import HDWallet


def create_parser():
	parser = argparse.ArgumentParser(
		description = '''Cкрипт, реализующий взаимодействие с api блокчейн эксплорера''',
		add_help = False
	)
	parent_group = parser.add_argument_group (title='Параметры')
	parent_group.add_argument(MapCmd.get_cmd(MapCmd.wallet), nargs='*', default=False, help=MapCmd.get_h(MapCmd.wallet))
	parent_group.add_argument(MapCmd.get_cmd(MapCmd.balance), action='store_const', const=True, default=False, help=MapCmd.get_h(MapCmd.balance))
	parent_group.add_argument(MapCmd.get_cmd(MapCmd.allIncTrns), action='store_const', const=True, default=False, help=MapCmd.get_h(MapCmd.allIncTrns))
	parent_group.add_argument(MapCmd.get_cmd(MapCmd.allOutTrns), action='store_const', const=True, default=False, help=MapCmd.get_h(MapCmd.allOutTrns))
	parent_group.add_argument(MapCmd.get_cmd(MapCmd.formatStr), nargs=1, type=str, default=False, help=MapCmd.get_h(MapCmd.formatStr))
	parent_group.add_argument(MapCmd.get_cmd(MapCmd.faq), action='help', help=MapCmd.get_h(MapCmd.faq))
	return parser


class CreaterWallet(object):

	@staticmethod
	def new_wallet(name):
		return HDWallet.create(name)

	@staticmethod
	def new_key(wallet):
		return wallet.new_key()

class CommandHandler(object):
	def __init__(self, commands):
		self.commands = commands
		self.format_str = '\t\tДата: {d}\n\t\tАдресс: {a}\n\t\tBTC: {s}\n'

	def process_input_data(self):
		wallets = self.commands[MapCmd.cut_prefix(MapCmd.wallet)]

		if wallets:
			self.process_general_key()
			self.process_wallets(wallets)
		else:
			if all(cmd is False for cmd in self.commands.values()):
				self.withdraw_ten_wallets()
			else:
				print ('Введите как минимум один кошелёк, или уберите все ключи, что бы отработал скрипт')

	def process_general_key(self):
		cmds = self.get_active_cmds()

		if MapCmd.cut_prefix(MapCmd.formatStr) in cmds:
			format_str = self.commands[MapCmd.cut_prefix(MapCmd.formatStr)][0]
			self.save_format_str(format_str)

	def process_wallets(self, wallets):
		all_info = {}
		for wallet in wallets:
			all_info[wallet] = self.get_info_wallet(wallet)
		self.output_info(all_info)

	def withdraw_ten_wallets(self):
		ten_name_wallet = [str(random.random()) for i in range(10)]
		for name in ten_name_wallet:
			w = CreaterWallet.new_wallet(name)
			k = CreaterWallet.new_key(w)
			print ('key: {}  balance: {}  adress: {}'.format(k.key_private, k.balance(), k.address))



	def get_active_cmds(self):
		wallets = MapCmd.cut_prefix(MapCmd.wallet)
		return list(filter(lambda x: self.commands[x] is not False and x is not wallets, self.commands.keys()))

	def get_info_wallet(self, wallet):
		info = []
		def_for_cmd = {
			MapCmd.cut_prefix(MapCmd.balance): self.get_balance, 
			MapCmd.cut_prefix(MapCmd.allIncTrns): self.get_inc_trns, 
			MapCmd.cut_prefix(MapCmd.allOutTrns): self.get_out_trns,
		}
		
		if self.validate_wallet(wallet):
			cmds = self.get_active_cmds()
			for cmd in cmds:
				func_w = def_for_cmd.get(cmd)
				if func_w:
					info.append(func_w(wallet))
		else:
			info.append('\tЭтот кошелек не валидный, проверьте его на наличие ошибки')

		return info

	def get_balance(self, wallet):
		balance = ApiBlockExplorer.get_balance(wallet)
		return '\tБаланс - {}'.format(self.get_btc(balance))

	def get_inc_trns(self, wallet):
		all_inc_trns = ApiBlockExplorer.inc_transactions(wallet)
		info = self.get_info_trns(all_inc_trns)
		return '\tВсе входящие транзакции - \n{}'.format('\n'.join(info))

	def get_out_trns(self, wallet):
		all_out_trns = ApiBlockExplorer.out_transactions(wallet)
		info = self.get_info_trns(all_out_trns)
		return '\tВсе исходящии транзакции - \n{}'.format('\n'.join(info))

	def get_info_trns(self, trns):
		info = []
		for trn in trns.values():
			for data in trn:
				date = self.get_strf_time(data['time'])
				adress = data['address']
				summ = data['value']
				info.append(self.format_str.format(d = date, a = adress, s = summ))
		return info

	def get_strf_time(self, time):
		time = datetime.fromtimestamp(int(time))
		return time.strftime('%Y-%m-%d')

	def get_btc(self, balance):
		return balance/100000000

	def save_format_str(self, format_str=None):
		if format_str is not None:
			self.format_str = format_str


	def validate_wallet(self, wallet):
		return True if ApiBlockExplorer.validate_address(wallet) else False

	def output_info(self, all_info):
		for wallet, info in all_info.items():
			print ('\nкошелек - {}'.format(wallet))
			for i in info:
				print ('{} '.format(i))



class MapCmd:
	wallet = 0
	balance = 1
	allIncTrns= 2
	allOutTrns = 3
	formatStr = 4
	faq = 5


	commands = {
		wallet: 'wallet',
		balance: '-b',
		allIncTrns: '-i',
		allOutTrns: '-o',
		formatStr: '-f',
		faq: '-h' 
	}

	commands_help = {
		wallet: 'Неименованный параметр. Служит для ввода кошельков',
		balance: 'Показать баланс кошельков',
		allIncTrns: 'Показать все входящие транзакции кошельков в формате дата, адрес, сумма',
		allOutTrns: 'Показать все исходящие транзакции кошельков в формате дата, адрес, сумма',
		formatStr: '''Параметр, который меняет формат вывода транзакций для ключей {},{}
		Форматированная строка поддерживает 3 переменные: {{d}}, {{a}}, {{s}} - дата, адрес, сумма'''.format(commands[allIncTrns], commands[allOutTrns]),
		faq: 'Краткая справка'
	}

	@staticmethod
	def cut_prefix(name):
		return MapCmd.get_cmd(name).replace('-', '')
	
	@staticmethod
	def get_cmd(name):
		return MapCmd.commands.get(name)

	@staticmethod
	def get_h(name):
		return MapCmd.commands_help.get(name)

def exit_script(*args):
	print ('Вы принудительно завершили программу')
	sys.exit()



if __name__ == '__main__':
	signal.signal(signal.SIGINT, exit_script)
	signal.signal(signal.SIGTERM, exit_script)
	parser = create_parser()
	commands = vars(parser.parse_args())
	handler = CommandHandler(commands)
	handler.process_input_data()
