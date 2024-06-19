from sf_query import had_activity, Account
from simple_salesforce import Salesforce
import json


def sf_login():
    with open(r"C:\Users\Bryan Edman\Documents\AMUncontacted\sf_creds.json") as f:
        sf_creds = json.load(f)
        sf = Salesforce(username=sf_creds["username"], password=sf_creds["password"], security_token=sf_creds["security_token"])
        return sf

if __name__ == "__main__":

    sf = sf_login()
    id = "0014U000031EAhZQAW"
    account = Account(id, "Matt Marvel", "ArronId", "Aaron Orr", True, "Silveus Scrub", True, "", True)
    yesNo = had_activity(sf, account)

    assert yesNo, "This account should show up as contacted!"
