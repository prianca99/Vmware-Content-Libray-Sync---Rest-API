# This python Script is used as an standalone exe in the SCO runbook.
# It is the second step of the automation which performs the Sync on the libraries taken from DB table .
# It uses Vcenter APIs to perform the sync

import requests
import json
import urllib3
import pyodbc
from datetime import datetime
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#Make DB connection

server = '<URL>:<PORT>'
database = '<DB NAME>'
username = '<USERNAME>'
password = '<PASSWORD>'
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = conn.cursor()

# This function performs the query to take one lib at a time whose status is 'pending'
# Once the function gets the lib. Sync is triggered and in the DB status is changed to 'Triggered'

def sync_subscribed_library(sessionid, payload):
    
    cookie_value = "sessionid=<id>;vmware-api-session-id=" + sessionid + ""
    lib_headers = {
        'cookie': cookie_value,
    }
    cursor.execute("select top(1) [SubscribedLibraryID] from <TABLE NAME> WHERE SyncStatus = ?", 'pending')
    date=datetime.now()
    synclibraryid=cursor.fetchone()
    if (synclibraryid is not None):
        synclibraryid=str(synclibraryid[0])
        print("proceesing with " +synclibraryid+ "at" +str(date))
        sync_url = "https://<VMware URL>/rest/com/vmware/content/subscribed-library/id:" + synclibraryid + "?~action=sync"
        try:
            print("in try")
            response4 = requests.request("POST", sync_url, headers=lib_headers, data=payload, verify=False)
            print(" sync triggered with ID: " + synclibraryid)
            date = datetime.now()
            cursor.execute("UPDATE <DB TABLE> SET SyncStatus = ?  WHERE SubscribedLibraryID = ?", 'Triggered', synclibraryid)
            cursor.execute("UPDATE <DB TABLE> SET SyncDate = ?  WHERE SubscribedLibraryID = ?", date, synclibraryid)
            cursor.commit()
            print("db update done")
        except requests.exceptions.ProxyError as e:
            print("in except")
            print(e)
            date2=datetime.now()
            cursor.execute("UPDATE <DB TABLE> SET SyncStatus = ?  WHERE SubscribedLibraryID = ?", 'Triggered',synclibraryid)
            cursor.execute("UPDATE <DB TABLE> SET SyncDate = ?  WHERE SubscribedLibraryID = ?", date2, synclibraryid)
            cursor.commit()
            print("db update done in except" )

        except Exception as e:
            print("in except")
            print(e)
            date2 = datetime.now()
            cursor.execute("UPDATE <DB TABLE> SET SyncStatus = ?  WHERE SubscribedLibraryID = ?", 'Triggered',synclibraryid)
            cursor.execute("UPDATE <DB TABLE> SET SyncDate = ?  WHERE SubscribedLibraryID = ?", date2, synclibraryid)
            cursor.commit()
            print("db update done in except")
    else:
        print("sync triggered for all")


# Main function call the AUTH API of Vcenter and pass the session id for sync to sync_subscribed_library()

def main():
    
    url = "https://<VMware URL>/rest/com/vmware/cis/session"

    payload = {}
    headers = {
        'Authorization': 'Basic <auth token>=',
        'Cookie': 'vmware-api-session-id=f<id>'
    }
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    response_body = response.json()
    sessionid = response_body['value']
    if (response.status_code == 200):
        sync_subscribed_library(sessionid, payload)
    else:
        print(response.status_code)
    

if __name__ == "__main__":
    main()
