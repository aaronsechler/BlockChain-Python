import subprocess
import json
import os
from web3 import Web3, middleware, Account
from pathlib import Path
from getpass import getpass
from bit import wif_to_key
from bit import PrivateKeyTestnet
#from dotenv import load_dotenv
from web3.middleware import geth_poa_middleware
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
from bit.network import NetworkAPI

from constants import *

#mnemonic = os.getenv('MNEMONIC', 'address canyon camera eternal churn matrix weather layer priority true picnic hat')

mnemonic = 'address canyon camera eternal churn matrix weather layer priority true picnic hat'



def derive_wallets(mnemonic, coin, numderive):

    command = f'./derive -g --mnemonic="{mnemonic}" --coin={coin} --numderive={numderive} --cols=path,address,privkey,pubkey --format=json'

    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()

    keys = json.loads(output)
    #print(keys)
    return keys

coins = {ETH:derive_wallets(mnemonic, ETH, 3), 
        BTCTEST:derive_wallets(mnemonic, BTCTEST, 3)}
#print(coins[BTCTEST][0]['privkey'])

def priv_key_to_account(coin, priv_key):
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    elif coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)
    

def create_tx(coin, account, to, amount):
    if coin == ETH:
        value = w3.toWei(amount, 'ether')
        gasEstimate = w3.eth.estimateGas(
            {"from":account.address, "to":to, "value": amount}
        )
        return{
            "from":account.address,
            "to":to,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(account.address),
            "chainId": w3.eth.chainId
            }
    elif coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])

def send_tx(coin, account, to, amount):
    if coin == ETH:
        tx = create_tx(coin, account, to, amount)
        signed = account.sign_transaction(tx)
        return w3.eth.sendRawTransaction(signed.rawTransaction)
    elif coin == BTCTEST:
        tx = create_tx(coin, account, to, amount)
        signed = account.sign_transaction(tx)
        return NetworkAPI.broadcast_tx_testnet(signed)

# UNKNOWN BTCTEST ERROR IS UNFIXED, ETH WORKS, NEED TO WRITE IT UP AND SCREENSHOT IT.
