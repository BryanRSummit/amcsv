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
    
def had_activity(sf, account):
    # Create a datetime object for October 1st, 2023
    cutoff = datetime(2023, 10, 1)
    contacted = False
    activityQuery = f"""
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
    account_records = sf.query_all(activityQuery)['records']

    for rec in account_records:
        act_date = parser.parse(rec["ActivityDate"])
        if act_date > cutoff:
            contacted = True
            account.contacted = True
    return contacted



def is_untouched(sf):
    # # Describe the Account object to get its fields
    # account_metadata = sf.Account.describe()
    # # Extract field names
    # field_names = [field['name'] for field in account_metadata['fields']]

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
            if not had_activity(sf, account):
                accounts_list[account.agentName] = []
                accounts_list[account.agentName].append(account)
        else:
            if not had_activity(sf, account):
                accounts_list[account.agentName].append(account)


    return accounts_list