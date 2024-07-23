from dateutil import parser
from datetime import datetime, timedelta
from dataclasses import dataclass
import re

@dataclass
class Agent:
    id: str
    username: str
    fname: str
    lname: str
    email: str

@dataclass
class Activity:
    id: str
    ownerId: str
    subject: str
    description: str
    activity_date: datetime

@dataclass
class Account:
    id: str
    name: str
    agentId: str
    agentName: str
    converted: bool
    account_type: str
    mapCreated: bool
    accountManagers: str
    contacted: bool



def eligible_contact(act):
    if act.subject == "Call" or act.subject == "Prospecting":
        return True
    return False

def get_opp_activity(sf, opId, cutOff):
    contacted = False
    # Create a datetime object for October 1st, 2023
    #cutoff = datetime(2023, 9, 1)

    oppActivityQuery = f"""
                SELECT
                    Id, 
                    Subject,
                    Description, 
                    WhatId, 
                    ActivityDate
                FROM Task
                WHERE WhatId = '{opId}'
    """
    opp_activity_records = sf.query_all(oppActivityQuery)['records']

    for op in opp_activity_records:
        act_date = parser.parse(op["ActivityDate"])
        if act_date > cutOff:
            contacted = True
            break
        
    return contacted

def get_contact_activity(sf, contactId, cutOff):
    contacted = False
    # Create a datetime object for October 1st, 2023
    #cutoff = datetime(2023, 9, 1)

    oppActivityQuery = f"""
                SELECT
                    Id, 
                    Subject,
                    Description, 
                    WhatId, 
                    ActivityDate
                FROM Task
                WHERE WhatId = '{contactId}'
    """
    opp_activity_records = sf.query_all(oppActivityQuery)['records']

    for op in opp_activity_records:
        act_date = parser.parse(op["ActivityDate"])
        if act_date > cutOff:
            contacted = True
            break
        
    return contacted



    
# Because people can put calls on accounts OR on Opportunities we have to query all 
# kinds of stuff here, hopefully it doesn't slow things down too much
def had_activity(sf, account, cutOff):
    contacted = False
    # Create a datetime object for October 1st, 2023
    #cutoff = datetime(2023, 9, 1)

    # get any activity on the account
    accountActivityQuery = f"""
                SELECT 
                    What.Name,
                    What.Id,
                    Id,
                    OwnerId, 
                    Subject,
                    Description,
                    ActivityDate
                FROM Task 
                WHERE WhatId IN ('{account.id}')
          """
    
    #get 2024 opportunity for this account to check for activity
    oppQuery = f"""
                SELECT
                    Id, 
                    Name, 
                    StageName, 
                    CloseDate, 
                    Amount
                FROM Opportunity
                WHERE AccountId = '{account.id}' AND Name LIKE '%2024%' 
          """
    #get contacts on the account
    contactQuery = f"""
                SELECT 
                    Id, 
                    AccountId,
                    Name,
                    OwnerId
                FROM Contact
                WHERE AccountId = '{account.id}'
            """
    

    account_activity_records = sf.query_all(accountActivityQuery)['records']
    opp_records = sf.query_all(oppQuery)['records']
    contact_records = sf.query_all(contactQuery)['records']


    # check activity on accounts 
    for rec in account_activity_records:
        act_date = parser.parse(rec["ActivityDate"])
        if act_date > cutOff:
            contacted = True
            account.contacted = True

    #don't do this part if we already found activity on account
    if contacted == False:
        #check if opportunity has recent activity
        for op in opp_records:
            contacted = get_opp_activity(sf, op["Id"], cutOff)
            if contacted == True:
                break

    #don't do this part if we already found activity on account
    if contacted == False:
        #check if opportunity has recent activity
        for contact in contact_records:
            contacted = get_contact_activity(sf, contact["Id"], cutOff)
            if contacted == True:
                break

        
    return contacted



def is_untouched(sf, cutOff):
    # Used to see Object fields
    account_metadata = sf.Contact.describe()
    # Extract field names
    field_names = [field['name'] for field in account_metadata['fields']]

    accountQuery = f"""
            SELECT 
                Id,
                Name,
                Agent__c,
                Agent_Name__c,
                Converted__c,
                Account_Type__c,
                Map_Created__c,
                Account_Managers__c,
                Called_by_Agent__c
            FROM Account  
            WHERE Converted__c = True AND Account_Type__c != 'Customer'
                """

    account_records = sf.query_all(accountQuery)['records']

    # break up into individual agents
    accounts_list = {}
    for a in account_records:
        account = Account(a["Id"], a["Name"], a["Agent__c"], a["Agent_Name__c"], a["Converted__c"], a["Account_Type__c"], a["Map_Created__c"], a["Account_Managers__c"], False)
        if account.agentName not in accounts_list:
            if not had_activity(sf, account, cutOff):
                accounts_list[account.agentName] = []
                accounts_list[account.agentName].append(account)
        else:
            if not had_activity(sf, account, cutOff):
                accounts_list[account.agentName].append(account)


    return accounts_list