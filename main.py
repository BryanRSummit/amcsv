from simple_salesforce import Salesforce
import json
from sf_query import is_untouched

def sf_login():
    with open(r"C:\Users\Bryan Edman\Documents\AMUncontacted\sf_creds.json") as f:
        sf_creds = json.load(f)
        sf = Salesforce(username=sf_creds["username"], password=sf_creds["password"], security_token=sf_creds["security_token"])
        return sf




if __name__ == "__main__":
    sf = sf_login()
    untouched_by_agent = is_untouched(sf)
    print("hey")