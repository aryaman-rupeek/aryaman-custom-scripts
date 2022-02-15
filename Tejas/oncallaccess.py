import ldap,datetime,dateutil,json,pytz,os
import requests as re

ADMIN_GROUPS_LIST = os.environ.get("ADMIN_GROUPS_LIST") 
LDAP_SEARCH_BASE_DN =os.environ.get("LDAP_SEARCH_BASE_DN") 
LDAP_HOST=os.environ.get("LDAP_HOST") 
LDAP_BINDUSER=os.environ.get("LDAP_BINDUSER") 
LDAP_BINDPASSWORD=os.environ.get("LDAP_BINDPASSWORD") 
DEVOPS_SCHEDULE_ID=os.environ.get("DEVOPS_SCHEDULE_ID")
USER_EXCEPTION_LIST=os.environ.get("USER_EXCEPTION_LIST")
PD_TOKEN = os.environ.get("PD_TOKEN")

ADMIN_GROUPS_LIST = [x.strip() for x in ADMIN_GROUPS_LIST.split(",")]
USER_EXCEPTION_LIST = [x.strip() for x in USER_EXCEPTION_LIST.split(",")]

headers={"accept": "application/vnd.pagerduty+json;version=2",
                    "authorization": f"Token token={PD_TOKEN}",
                    "content-type": "application/json"}


def getPDUsersDict(schedule_id,headers):
    url = f"https://api.pagerduty.com/schedules/{schedule_id}/users"
    response = re.request("GET", url, headers=headers)
    
    onPDUserDict={}
    for user in response.json()['users']:
        if user['self'] is not None:
            onPDUserDict[user['id']]={"name": user['name'],"email": user['email']}
              
    return onPDUserDict

def getOnCallUser(schedule_id,headers):
    
    url = "https://api.pagerduty.com/oncalls"
    onCallUser = {}
    querystring = {"schedule_ids[]": schedule_id}
    response = re.request("GET", url, headers=headers,params=querystring)
    onCallUser['id'] = response.json()['oncalls'][0]['user']['id']
    onCallUser['name']=response.json()['oncalls'][0]['user']['summary']
    
    return onCallUser

def ldapAdd(conn,userdn,groupcn):
    GROUP_DN=f"CN={groupcn},OU=AWS,OU=Tech_Groups,OU=System_Groups,OU=Groups,OU=Rupeek_OU,DC=ad,DC=rupeek,DC=net"
    conn.modify_s(
    GROUP_DN,
    [
        (ldap.MOD_ADD, 'member', [userdn.encode("utf-8")]),
    ],
    )
    print({"rpk":{"log":f"User is added to {groupcn} AWS admin group"}})

    
def ldapRemove(conn,userdn,groupcn):
    GROUP_DN=f"CN={groupcn},OU=AWS,OU=Tech_Groups,OU=System_Groups,OU=Groups,OU=Rupeek_OU,DC=ad,DC=rupeek,DC=net"
    conn.modify_s(
    GROUP_DN,
    [
        (ldap.MOD_DELETE, 'member', [userdn.encode("utf-8")]),
    ],
    )
    print({"rpk":{"log":f"User is removed from {groupcn} AWS admin group"}})

def getLDAPUserDetails(conn,user):
    
    search_filter=f"sAMAccountName={user}"
    result=connect.search_s(LDAP_SEARCH_BASE_DN,ldap.SCOPE_SUBTREE,search_filter,['memberOf'])
#     user_dn=result[0][0]
    
    return result
    
    
connect = ldap.initialize(LDAP_HOST)
connect.simple_bind_s(LDAP_BINDUSER,LDAP_BINDPASSWORD)



#get onuser from pagerduty

onCallUser=getOnCallUser(DEVOPS_SCHEDULE_ID,headers)

#get all users in the team
devopsUsersDict = getPDUsersDict(DEVOPS_SCHEDULE_ID,headers)

#Check user for oncall and take appropriate access action
for userid,uservalues in devopsUsersDict.items():

    name = uservalues['name']
    email = uservalues['email']
    sAMAccountName = uservalues['email'].split('@')[0]
    
    if email not in USER_EXCEPTION_LIST:
        ldapDetails = getLDAPUserDetails(connect,sAMAccountName)
        userDN = ldapDetails[0][0]
        userGroups = ldapDetails[0][1]['memberOf']
        
        if userid == onCallUser['id']:
     
            for adminGroup in ADMIN_GROUPS_LIST:
                if adminGroup in ','.join([x.decode('utf-8') for x in userGroups]):
                    print({"rpk":{"log":{name:{adminGroup: "1","on-call": "1","action":"NA"}}}})
                else:
                    print({"rpk":{"log":{name:{adminGroup: "0","on-call": "1","action": f"Add user to {adminGroup}"}}}})
                    ldapAdd(connect,userDN,adminGroup)
        else:
            for adminGroup in ADMIN_GROUPS_LIST:
                if adminGroup in ','.join([x.decode('utf-8') for x in userGroups]):
                    print({"rpk":{"log":{name:{adminGroup: "1","on-call": "0", "action": f"Remove user from {adminGroup}"}}}})
                    ldapRemove(connect,userDN,adminGroup)
                else:
                    print({"rpk":{"log":{name:{adminGroup: "0","on-call": "0","action":"NA"}}}})
            

            
                
        
        
    
