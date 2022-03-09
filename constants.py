# constants file
import numpy as np

# Generated accounts for testing
# creator user declared account mnemonics
creator_mnemonic = 'armed note crew promote scheme luxury impulse genius manage mutual cash local imitate flight zero attend expose device amazing guilt clap leader snow abandon artefact'

# array of pre-generated and funded users
generated_test_users = np.array(
    [
        {
            'name': 'User1',
            'private_key': '5Xi+rZAPUvK1nFYDjWWn/H7Zxlsjm8Do8XK9kjAk/IPtEquYsn7a1cIWwB0W/ihucolAoY1KtBrFD2xe7v/+HA=='
        },
        {
            'name': 'User2',
            'private_key': 'CyHrncs+Fn+oZXhL/RRehK+Cr9WuWf6HuHaY7UkJlNL/ikqUVLXBbBmEZlG8pYGL0SJ/lB0Irykd4Fh/y+/BEA=='
        },
        {
            'name': 'User3',
            'private_key': 'HqzLENGS8QCRQFhtoRVbhipeha/8AJTxLDn30Yvv/MfchaTQk35PRmVRJni6xFhhkrAtoPw5P0t92BQbQiuMbQ=='
        },
    ])

# Algorand parameters
# user declared algod connection parameters. Node must have EnableDeveloperAPI set to true in its config
algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

# app id, to reuse an old app
app_id_global = 76824854

# The average Algorand block production time is about 4.5 seconds per block
block_speed = 4.5
