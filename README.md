# Vmware-Content-Libray-Sync---Rest-API
To ensure that your subscribed library displays the latest content of the published library, you can manually initiate a synchronization task.
Python scripts to push the syncronization on the subscireb content libraries in the VMware.
  1. LibrarytoDB.py: This script will fetch the subscribed content libraries from the VMware Content Libray Rest API and push it into database. This will be used tosince we are triggering the sync at the interval of 2 hours.
  
  2. LibrarySync.py: This script will take the subscribed library one by one by its Status and will trigger the sync.
