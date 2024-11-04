import sys, os

sys.path.append('./')
from ecdh.backend import Backend
from ecdh.client import Client
from ecdh.setup import setup

# read env CA_ARN
if 'CA_ARN' not in os.environ:
    print("Please set CA_ARN")
    exit(1)
ca_arn = os.environ['CA_ARN']

apc_client_ca_key_arn, apc_pgk_arn, apc_pek_arn, apc_ecdsa_key_arn = setup(ca_arn)

backend = Backend(ca_arn, apc_pek_arn, apc_client_ca_key_arn, apc_pgk_arn, apc_ecdsa_key_arn)

client = Client()

pan = "1234567889012345"
print("FLOW #1: Generating a random PIN for CC and revealing it for the user to memorize")
new_pin = client.pin_reset(pan, backend)
new_pin_pvv = backend.pvv
print("New Pin is %s" % new_pin)


set_pin = "1234"
print("FLOW #2: Setting an arbitrary PIN %s and obtaining it's PVV and encrypted pinblock" % 1234)
client.set_pin(set_pin, pan, backend)
set_pin_pvv = backend.pvv
encrypted_pinblock = backend.tmp_pek_pinblock
print("Encrypted pinblock is %s, PVV is %s" % (encrypted_pinblock, set_pin_pvv))

print("FLOW #3: Revealing the PIN hidden in Encrypted Pinblock")
revealed_pin = client.pin_reveal(encrypted_pinblock, pan, backend)
print("Revealed PIN %s" % revealed_pin)
if revealed_pin == set_pin:
    print("OK: Revealed PIN == SET PIN")
else:
    print("ERROR")

print("Please remember to execute tear_down.py if you want to remove the assets created")