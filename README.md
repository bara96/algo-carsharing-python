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
<code>./sandbox start testnet</code>

## Python environment and dependencies
Install the required dependencies for the project.  
Using a Python virtual environment (**venv**) is recommended to do this.  
The following commands will activate the virtual environment and then install all dependencies, including PyTeal and the Algorand Python SDK.

Setup Python environment (one time).  
<code>python3 -m venv venv</code>  

Activate venv. Replace bin with Scripts on Windows.  
<code>. venv/bin/activate</code>

Make sure that you have pip installed.
If not, you can install it like this:  
<code>sudo apt install python3-pip</code>  

Now install all requirements.  
<code>pip3 install -r requirements.txt</code>

## Account Management
Use [goal](https://developer.algorand.org/docs/clis/goal/goal/) in order to create wallet and manage accounts.

### Useful commands
**Wallet:**
- <code>goal wallet new</code> <small>Create a new wallet</small>
- <code>goal wallet new</code> <small>List wallets managed by kmd</small>

**Account:**
- <code>goal account list </code> <small>Show the list of Algorand accounts on this machine</small>
- <code>goal account new </code> <small>Create a new account</small>
- <code>goal account -f [name] </code> <small>Set the account with this name to be the default account</small>
- <code>goal account info -a [address]</code> <small>Retrieve information about the assets and applications belonging to the specified account</small>
- <code>goal account import -m [menmonic]</code> <small>Import an existing account</small>
- <code>goal account export -a [address]</code> <small>Export an account key for use with account import</small>
- <code>goal account delete -a [address]</code> <small>Delete an account</small>

**App:**
- <code>goal goal app info --app-id [id]</code> <small>Look up current parameters for an application</small>
- <code>goal goal app clear --app-id [id]</code> <small>Clear out an application's state in your account</small>
- <code>goal goal app delete --app-id [id]</code> <small>Delete an application</small>

**Logging**
- <code>goal logging enable -n [nodeName]</code> <small>Enable Algorand remote logging</small>
- <code>goal logging disable -n [nodeName]</code> <small>Disable Algorand remote logging</small>



## Funding Account
Follow [this guide](https://developer.algorand.org/docs/sdks/go/?from_query=fund#fund-account) to fund a test account before perform transactions.
- [Algorand Testnet Dispenser](https://dispenser.testnet.aws.algodev.network/): fund test account
- [AlgoExplorer](https://algoexplorer.io/api-dev/v2): search for transactions (set on testnet)


##Test Wallet
In order to test this application a test Wallet is created with some funded account to use:
- **wallet name:** carsharing-testnet
- **wallet password:** carsharing

**Note**: this wallet is available only on sandbox mode with testnet configuration.



