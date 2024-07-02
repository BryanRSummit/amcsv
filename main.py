from simple_salesforce import Salesforce
import os
import json
import pickle
import hashlib
import csv
import time
from dateutil import parser
from cryptography.fernet import Fernet
from sf_query import is_untouched


def verify_password(stored_password, provided_password, salt):
    hash_obj = hashlib.sha256()
    hash_obj.update(bytes.fromhex(salt) + provided_password.encode('utf-8'))
    return stored_password == hash_obj.digest().hex()


def sf_login():
    cwd = os.getcwd()
    cred_path = os.path.join(cwd, "encrypted_credentials.json")
    key_path = os.path.join(cwd, "key.key")

    # Load the key
    with open(key_path, 'rb') as key_file:
        key = key_file.read()

    cipher_suite = Fernet(key)

    # Load credentials from JSON file
    with open(cred_path, 'r') as f:
        creds = json.load(f)

    # Decrypt the password and token
    encrypted_password = creds['encrypted_password'].encode('utf-8')
    encrypted_sec_token = creds["encrypted_sec_token"].encode('utf-8')
    decrypted_password = cipher_suite.decrypt(encrypted_password).decode('utf-8')
    decrypted_sec_token = cipher_suite.decrypt(encrypted_sec_token).decode('utf-8')

    sf = Salesforce(username=creds["username"], password=decrypted_password, security_token=decrypted_sec_token)
    return sf



if __name__ == "__main__":
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

    start_time = time.time()

    # Check if the file exists
    if os.path.isfile(pickle_file):
        print(f"The file '{pickle_file}' exists. Using it for data. . . ")
        # Load the dictionary from the file
        with open(pickle_file, 'rb') as file:
            agent_dict = pickle.load(file)
    else:
        print(f"Creating '{pickle_file}'. Executing Query with cut off date of {cutoffDate}.\nRunning. . . ")
        agent_dict = is_untouched(sf, cut_off_date)

        # Save the dictionary to the file
        with open(pickle_file, 'wb') as file:
            pickle.dump(agent_dict, file, protocol=pickle.HIGHEST_PROTOCOL)
    # ------------------------------------- Pickle file handling -------------------------

    os.makedirs(dirName, exist_ok=True)

    column_names = ["Account Id", "Account Name", "Account Type", "Account Link"]

    for agent, accounts in agent_dict.items():
        csv_filename = f"{agent}_uncontacted.csv"
        csv_file_path = os.path.join(dirName, csv_filename)

        with open(csv_file_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=column_names)
            writer.writeheader()

            for account in accounts:
                account_dict = {
                    "Account Id": account.id,
                    "Account Name": account.name,
                    "Account Type": account.account_type,
                    "Account Link": f"https://reddsummit.lightning.force.com/lightning/r/Account/{account.id}/view",
                }
                writer.writerow(account_dict)

    end_time = time.time()
    total_time = end_time - start_time
    print(f"CSV files created successfully. Process took {total_time} seconds")

    end = input("\nThank you for using this tool!\nCreated by Bryan Edman\n2024\n\nPress Enter to close. . . ")