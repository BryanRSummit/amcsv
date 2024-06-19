from simple_salesforce import Salesforce
import os
import json
import pickle
import csv
import time
from dateutil import parser
from datetime import datetime, timedelta
from sf_query import is_untouched

def sf_login():
    with open(r"C:\Users\Bryan Edman\Documents\AMUncontacted\sf_creds.json") as f:
        sf_creds = json.load(f)
        sf = Salesforce(username=sf_creds["username"], password=sf_creds["password"], security_token=sf_creds["security_token"])
        return sf




if __name__ == "__main__":
    start_time = time.time()
    sf = sf_login()




    create = ""
    dirName = input("Name a Directory to save the CSV files to. ")

    # Get the current working directory
    cwd = os.getcwd()
    # Check if there are any .pickle files in the current directory
    pickle_files = [f for f in os.listdir(cwd) if f.endswith(".pickle")]
    if not pickle_files:
        create = "create"
    else:
        create = input("Would you like to run with the data from another run or create a new query?\nType create for new enter otherwise. ")
 
    

    if create == "create":

        cutoffDate = input("Enter the cut off date for last activity in the form m-d-yyyy ")
        cut_off_date = parser.parse(cutoffDate)
        # create mew pickle file with meaningful name
        pickle_file = f'{dirName}_{cutoffDate}.pickle'
    else:
        tempPickleFile = ""
        while not os.path.isfile(tempPickleFile):
            tempPickleFile = input("Choose the pickle file you would like to use. ")

        pickle_file = tempPickleFile
    # ------------------------------------- Pickle file handling -------------------------


    # Check if the file exists
    if os.path.isfile(pickle_file):
        print(f"The file '{pickle_file}' exists. Using it for data. . . ")
        # Load the dictionary from the file
        with open(pickle_file, 'rb') as file:
            agent_dict = pickle.load(file)
    else:
        print(f"Creating '{pickle_file}'. Executing Query with cut off date of {cutoffDate}.\nRunning. . . ")
        # Create your dictionary here
        agent_dict = is_untouched(sf, cut_off_date)

        # Save the dictionary to the file
        with open(pickle_file, 'wb') as file:
            pickle.dump(agent_dict, file, protocol=pickle.HIGHEST_PROTOCOL)
    # ------------------------------------- Pickle file handling -------------------------


    # Create the directory for the CSV files
    os.makedirs(dirName, exist_ok=True)

    column_names = ["Account Name", "Account Link", "Account Type", "Map Created", "Account Managers"]
    # Loop through each agent in the dictionary
    for agent, accounts in agent_dict.items():
        # Create a CSV file for the agent
        csv_filename = f"{agent}_uncontacted.csv"
        csv_file_path = os.path.join(dirName, csv_filename)

        with open(csv_file_path, "w", newline="") as csvfile:
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
    end_time = time.time()
    total_time = end_time - start_time
    print(f"CSV files created successfully. Process took {total_time}")