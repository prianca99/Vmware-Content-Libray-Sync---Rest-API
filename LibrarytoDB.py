
# It is first step of the VMware Template Sync.
# This will insert the list of all the subscribed content libraries to the DB Table 

# The script has two functions: 1) Get Subscribed Library 2) Insert Library to DB

import requests
import json
import urllib3
import pyodbc
from datetime import datetime
import sys
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


#DB Connection
server = '<DBURL>:<PORT>'
database = '<DB NAME>'
username = '<USERNAME>'
password = '<PASSWORD>'
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = conn.cursor()

# Below function calls takes the session ID from Vcenter Content API call and fetch the subscribed libraries

def get_subscribed_library(sessionid, payload, sync_lib_name, testdict):
    cookie_value = "sessionid=<id>;vmware-api-session-id=" + sessionid + ""
    lib_headers = {
        'cookie': cookie_value,
    }
    subscribed_library_url = "https://<VMwareURL>/rest/com/vmware/content/subscribed-library"
    response2 = requests.request("GET", subscribed_library_url, headers=lib_headers, data=payload, verify=False)
    if (response2.status_code == 200):
        subscribed_library = response2.json()['value']
        if (len(subscribed_library) > 0):
            get_subscribed_library_ids(lib_headers, subscribed_library, payload, sync_lib_name, testdict)
        else:
            print("no subscribed library")


# List of all the subscribed libraries passed to this function from 'get_subscribed_library()'

def get_subscribed_library_ids(lib_headers, subscribed_library, payload, sync_lib_name, testdict):
    synclibraryid = ''
    for id in subscribed_library:
        synclibitemurl = "https://<VMware URL>/rest/com/vmware/content/subscribed-library/id:" + id
        response3 = requests.request("GET", synclibitemurl, headers=lib_headers, data=payload, verify=False)
        #print(response3.status_code)
        if (response3.status_code == 200):
            synclibraryid = response3.json()['value']['id']
            synclibraryname = response3.json()['value']['name']
            testdict[synclibraryname] = synclibraryid
        elif (response3.status_code == 404):
            print("subscribed library" + id + " not found")
        else:
            print(response3.status_code)



# Main function calls the API get request to VCenter Session and then calls the function to get the libraries

def main():

    testdict = {}
    url = "https://<VMware URL>/rest/com/vmware/cis/session"

    payload = {}
    headers = {
        'Authorization': 'Basic <Auth token>',
        'Cookie': 'vmware-api-session-id=<id>'
    }
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    print(response)

    response_body = response.json()
    #print(response_body)
    sessionid = response_body['value']
    #print(sessionid)
    # print(type(sessionid))
    if (response.status_code == 200):
        get_subscribed_library(sessionid, payload, sync_lib_name, testdict)
    else:
        print(response.status_code)

    libdata={}
    libdate=date=datetime.now().date()
    libdata[libdate]=testdict

    date=datetime.now()
    status='pending'
    
    # This testdict has the data from function 'get_subscribed_library' . Data will be inserted to DB
    for i in testdict:
        libname=i
        libid=testdict[i]
        cursor.execute("INSERT INTO <DBTABLE>(SubscribedLibrary,SubscribedLibraryID,SyncStatus,StartDate) VALUES (?,?,?,?)", (libname,libid,status,date))
        cursor.commit()
    
    print(libdata)
if __name__ == "__main__":
    main()
