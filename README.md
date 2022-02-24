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


