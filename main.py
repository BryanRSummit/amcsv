from simple_salesforce import Salesforce
import os
import json
import pickle
import csv
from sf_query import is_untouched

def sf_login():
    with open(r"C:\Users\Bryan Edman\Documents\AMUncontacted\sf_creds.json") as f:
        sf_creds = json.load(f)
        sf = Salesforce(username=sf_creds["username"], password=sf_creds["password"], security_token=sf_creds["security_token"])
        return sf




if __name__ == "__main__":
    sf = sf_login()

    # ------------------------------------- Pickle file handling -------------------------
    # Path to the pickle file
    pickle_file = 'agents.pickle'
    # Check if the file exists
    if os.path.isfile(pickle_file):
        print(f"The file '{pickle_file}' already exists.")
        # Load the dictionary from the file
        with open(pickle_file, 'rb') as file:
            agent_dict = pickle.load(file)
    else:
        print(f"The file '{pickle_file}' does not exist.")
        # Create your dictionary here
        untouched_by_agent = is_untouched(sf)

        # Save the dictionary to the file
        with open(pickle_file, 'wb') as file:
            pickle.dump(untouched_by_agent, file, protocol=pickle.HIGHEST_PROTOCOL)
    # ------------------------------------- Pickle file handling -------------------------


    column_names = ["Account Name", "Account Link", "Account Type", "Map Created", "Account Managers"]
    # Loop through each agent in the dictionary
    for agent, accounts in agent_dict.items():
        # Create a CSV file for the agent
        csv_filename = f"{agent}_uncontacted.csv"
        with open(csv_filename, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=column_names)
            
            # Write the column names as the header
            writer.writeheader()
            
            # Write each account as a row in the CSV file
            for account in accounts:
                account_dict = {
                    "Account Name": account.name,
                    "Account Link": f"https://reddsummit.lightning.force.com/lightning/r/Account/{account.id}/view",
                    "Account Type": account.account_type,
                    "Map Created": account.mapCreated,
                }
                writer.writerow(account_dict)

    print("CSV files created successfully.")