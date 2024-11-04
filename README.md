
# AWS Payment Crypto ECDH Pin Set/Reveal flows

Setup

Generate a Python Virtual Environment and install required libraries
```
python3 -m venv .venv
pip3 install -r requirements.txt
```

Generate an AWS Private CA, this has a US$ 50 USD/month cost
```
python3 payment_crypto/setup_ca.py
```
The output of this script will be a line `export CA_ARN='xxxxxxxxx'`, execute that line to continue.

Simulate the three Flows of this Demo
```
python3 payment_crypto/main.py
```

Clean up resources (including CA)
```
python3 payment_crypto/tear_down.py
```

