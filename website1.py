check_auth.py
import sys
import configparser
import requests
from requests.auth import HTTPBasicAuth
from requests_ntlm import HttpNtlmAuth

try:
    # Try to import requests_negotiate_sspi (Windows)
    from requests_negotiate_sspi import HttpNegotiateAuth
except ImportError:
    # If on Linux, use requests-kerberos
    from requests_kerberos import HTTPKerberosAuth, REQUIRED

# Read the configuration file
config = configparser.ConfigParser()
config.read('input_config.ini')

# Fetch the URL, username, password, and expected content
url = config['AUTH']['url']
username = config['AUTH']['username']
password = config['AUTH']['password']
expected_content = config['EXPECTED']['content']

# Function to detect authentication type and perform the check
def detect_and_check_auth():
    auth_types = [
        ('Basic', HTTPBasicAuth(username, password)),
        ('NTLM', HttpNtlmAuth(username, password)),
    ]

    # Add Negotiate (Kerberos) authentication based on platform
    try:
        auth_types.append(('Negotiate', HttpNegotiateAuth()))
    except NameError:
        auth_types.append(('Negotiate', HTTPKerberosAuth(mutual_authentication=REQUIRED)))

    # Try each authentication method
    for auth_name, auth_method in auth_types:
        try:
            print(f"Trying {auth_name} authentication...")

            response = requests.get(url, auth=auth_method, verify=False)
            
            # Check if authentication succeeded
            if response.status_code == 200:
                print(f"Authentication successful with {auth_name}.")

                # Check for expected content in the response
                if expected_content in response.text:
                    print(f"OK - Expected content '{expected_content}' found in the page.")
                    return 0  # Nagios OK status
                else:
                    print(f"CRITICAL - Expected content '{expected_content}' NOT found in the page.")
                    return 2  # Nagios CRITICAL status

            elif response.status_code == 401:
                print(f"Authentication failed with {auth_name}. Status Code: {response.status_code}")
            else:
                print(f"Unexpected status code {response.status_code} with {auth_name}.")
        
        except Exception as e:
            print(f"Error occurred with {auth_name}: {e}")

    print("CRITICAL - Authentication failed for all methods.")
    return 2  # Nagios CRITICAL status

if __name__ == "__main__":
    sys.exit(detect_and_check_auth())



input_config.ini

[AUTH]
url = https://yourwebsite.com/path
username = your_username
password = your_password

[EXPECTED]
content = Success
