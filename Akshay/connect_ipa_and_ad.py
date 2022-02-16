import python_freeipa
from python_freeipa import ClientMeta
import os
import urllib3
import json
# import sys
import ldap3
from ldap3 import Server, Connection, ALL, MODIFY_REPLACE, ALL_ATTRIBUTES, BASE, LEVEL, SUBTREE, FIRST
from ldap3.core.exceptions import *

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
users = os.environ["users"].split(',')
groups = os.environ["groups"].split(',')
# groups = sys.argv[1].split(',')
# users = sys.argv[2].split(',')

def get_list_of_ipa_users():

    os.environ["PYTHONHTTPSVERIFY"] = "0"

    ipa_server = 'ipa-service-prod-03.internal.rupeek.co'
    ipa_user = os.environ["ipa_user"]
    ipa_password = os.environ["ipa_password"]

    ipa_client = ClientMeta(ipa_server, verify_ssl=False)
    ipa_client.login(ipa_user, ipa_password)


def get_list_of_ad_users():

    os.environ["PYTHONHTTPSVERIFY"] = "0"

    ad_server = ldap3.Server('ad.rupeek.net',use_ssl=False)
    ad_user = os.environ["ad_user"]
    ad_password = os.environ["ad_password"]

    ad_connection = ldap3.Connection(ad_server,user=ad_user,password=ad_password,auto_bind=True)

    if not ad_connection.bind():
        print('error in bind', ad_connection.result)

    ad_connection.search(
        search_base='CN=users,CN=accounts,DC=internal,DC=rupeek,DC=co',
        search_filter='(objectClass=uid)',
        search_scope=BASE,
        attributes=ALL_ATTRIBUTES
    )

    for entry in ad_connection.entries:
        print(entry.member.values)


# for group in groups:
#     group_stat = ipa_client.group_find(o_cn=group)
#     if group_stat['count'] == 1:
#         print("group already exists")
#     else:
#         print("group doesn't exist. Creating.....")
#         ipa_client.group_add(a_cn=group, o_description='This group is managed by AD')
#     for user in users:
#         user = user.replace('@rupeek.com', '')
#         try:
#             ipa_client.group_add_member(group, o_ipaexternalmember=None, o_all=True, o_raw=False, o_no_members=False, o_user=user, o_group=None, o_service=None)
#             print(f"User {user} added to group {group} successfully")
#         except python_freeipa.exceptions.DuplicateEntry as e:
#             print(f"User {user} already added to group {group}")
