
   
'''
 # @ Author: killari.kumar
 # @ Create Time: 2021-02-02 12:51:50
 # @ Description: Add users to IPA groups
 '''

######Add existing IPA users to IPA groups######

from python_freeipa import ClientMeta
import python_freeipa
import os
import urllib3
# import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
users = os.environ["users"].split(',')
groups = os.environ["groups"].split(',')
# groups = sys.argv[1].split(',')
# users = sys.argv[2].split(',')

os.environ["PYTHONHTTPSVERIFY"] = "0"

ipa_server = 'ipa-service-prod-03.internal.rupeek.co'
ipa_user = os.environ["ipa_user"]
ipa_password = os.environ["ipa_password"]

ipa_client = ClientMeta(ipa_server, verify_ssl=False)
ipa_client.login(ipa_user, ipa_password)
for group in groups:
    group_stat = ipa_client.group_find(o_cn=group)
    if group_stat['count'] == 1:
        print("group already exists")
    else:
        print("group doesn't exist. Creating.....")
        ipa_client.group_add(a_cn=group, o_description='This group is managed by AD')
    for user in users:
        user = user.replace('@rupeek.com', '')
        try:
            ipa_client.group_add_member(group, o_ipaexternalmember=None, o_all=True, o_raw=False, o_no_members=False, o_user=user, o_group=None, o_service=None)
            print(f"User {user} added to group {group} successfully")
        except python_freeipa.exceptions.DuplicateEntry as e:
            print(f"User {user} already added to group {group}")
