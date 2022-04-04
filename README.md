# Algo Carsharing
Smart Contract developed in [PyTeal](https://developer.algorand.org/docs/get-details/dapps/pyteal/) to build a dApp for car sharing in Algorand Blockchain


# Requirements
- [Python3.6 or higher](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/products/docker-desktop)
- [Docker Compose](https://docs.docker.com/compose/)

## Sandbox environment
In order to deploy any transaction on Algorand Blockchain you need first of all setup an Algorand node.  
You can easily setup an Algorand **sandbox** node following the [official guide](https://github.com/algorand/sandbox#algorand-sandbox) or following [this](https://developer.algorand.org/docs/get-started/dapps/pyteal/#install-sandbox) tutorial.  

We'll use the **Testnet** sandbox:  
`./sandbox up testnet`

On tesntet the indexer is not enabled, in order to use it you can switch on release sandbox:
`./sandbox up release`

## Python environment and dependencies
Install the required dependencies for the project.  
Using a Python virtual environment (**venv**) is recommended to do this.  
The following commands will activate the virtual environment and then install all dependencies, including PyTeal and the Algorand Python SDK.

Setup Python environment (one time).  
`python3 -m venv venv`  

Activate venv. Replace bin with Scripts on Windows.  
`. venv/bin/activate`

Make sure that you have pip installed.
If not, you can install it like this:  
`sudo apt install python3-pip`

Now install all requirements.  
`pip3 install -r requirements.txt`

## Env and Constants
Copy the `.env.example` into `.env`  
On `constants.py` set the correct account to use from `assets`.

## Account Management
Use [goal](https://developer.algorand.org/docs/clis/goal/goal/) in order to create wallet and manage accounts.

### Useful commands
**Wallet:**
- `goal wallet new` <small>Create a new wallet</small>
- `goal wallet new` <small>List wallets managed by kmd</small>

**Account:**
- `goal account list ` <small>Show the list of Algorand accounts on this machine</small>
- `goal account new ` <small>Create a new account</small>
- `goal account -f [name] ` <small>Set the account with this name to be the default account</small>
- `goal account info -a [address]` <small>Retrieve information about the assets and applications belonging to the specified account</small>
- `goal account import -m [menmonic]` <small>Import an existing account</small>
- `goal account export -a [address]` <small>Export an account key for use with account import</small>
- `goal account delete -a [address]` <small>Delete an account</small>

**App:**
- `goal goal app info --app-id [id]` <small>Look up current parameters for an application</small>
- `goal goal app clear --app-id [id] -f [account]` <small>Clear out an application's state in your account</small>
- `goal goal app delete --app-id [id]` <small>Delete an application</small>

**Logging**
- `goal logging enable -n [nodeName]` <small>Enable Algorand remote logging</small>
- `goal logging disable -n [nodeName]` <small>Disable Algorand remote logging</small>


## Funding Account
Follow [this guide](https://developer.algorand.org/docs/sdks/go/?from_query=fund#fund-account) to fund a test account before perform transactions.
- [Algorand Testnet Dispenser](https://dispenser.testnet.aws.algodev.network/): fund test account
- [AlgoExplorer](https://algoexplorer.io/api-dev/v2): search for transactions (set on testnet)


##Test Wallet
In order to test this application a local test Wallet is created with some funded account to use:
- **wallet name:** carsharing-testnet
- **wallet password:** carsharing

You can see the funded account on [constants.py](constants.py) or into [assets/accounts.xlsx](assets/Accounts.xlsx).  
Commands to create a wallet and import funded users are written on [create_wallet.txt](create_wallet.txt).

**Note**: this wallet is available only on sandbox mode with testnet configuration.



