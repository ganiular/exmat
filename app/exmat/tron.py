from tronpy import Tron
from tronpy.keys import PrivateKey

client = Tron(network='shasta')
address1 = 'TG7WXMwJLUfaP9MP4PZbqSHYPrHKiRbbwg'
private_key = PrivateKey(bytes.fromhex('59bf4c55fbf47402e22226fe50f5b2d52f3053f142e56a955a2122a0603ea447'))

address2 = 'TWF4VvLtMdc3DB4a8dfyZPBXmLC5vGZZKy'
private_key2 = PrivateKey(bytes.fromhex('a402430b0b8ed0a0e43eb9368e73d28d953532d7bfe8a56a6e6c11a422f5906a'))
print("account1:",client.get_account_balance(address1))
print("account2:",client.get_account_balance(address2))

txn = (
    client.trx.transfer(address1, address2, 10_000_000)
    .memo('http://www.exmat.io exmat.io test tranfer')
    .build()
    .sign(private_key)
)
txn.broadcast().wait()
