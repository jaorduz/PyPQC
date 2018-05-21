#!/usr/bin/env python
from __future__ import print_function
import os
import sys


def _decode_line(line):
	pair = line.split('=')
	return pair[0], pair[1].decode('hex')


def pqc_cli_api(cli_path, subcmd, *args):
	hex_args = [_.encode('hex') for _ in args]
	cmdline = ' '.join([cli_path, subcmd, ' '.join(hex_args)])
	res = os.popen(cmdline).read()
	return dict(map(_decode_line, res.splitlines()))


class PQCBase(object):
	def __init__(self, cli_path):
		self._cli_path = cli_path

	def api(self, cmd, *args):
		return pqc_cli_api(self._cli_path, cmd, *args)


class PQCSign(PQCBase):
	def __init__(self, cli_path):
		super(PQCSign, self).__init__(cli_path)

	def keypair(self):
		res = self.api('sign-gen')
		return res['PK'], res['SK']

	def sign(self, sk, message):
		return self.api('sign', sk, message)['SM']

	def open(self, pk, signed_message):
		return self.api('sign-open', pk, signed_message)['M']


if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("Usage: %s <./path/to/pqc_cli> cmd [arg [arg ...]]" % (sys.argv[0],))
		sys.exit(1)

	res = pqc_cli_api(sys.argv[1], sys.argv[2], *sys.argv[3:])

	for k, v in res.items():
		print(k, '=', v.encode('hex'))

	x = PQCSign(sys.argv[1])
	pk, sk = x.keypair()
	msg = os.urandom(128)
	smsg = x.sign(sk, msg)
	cmsg = x.open(pk, smsg)
	print(msg == cmsg)