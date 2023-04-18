from pybliometrics.scopus.utils import config

# YOUR API KEY GOES HERE!
config['Authentication']['APIKey'] = "YOUR API KEY HERE"

# Show the keys
print(f"API Key set to: {config['Authentication']['APIKey']}")
