# -*- coding: utf-8 -*-

import re
from Globals import globalUsers
from Globals import globalUserCount
from Globals import ServerUser

from base64 import b64encode, b64decode
from datetime import datetime
from os.path import exists

from Config import readFromConfig
from Database import Database
from Utilities.Packet import Packet

from urllib3 import *

db = Database()


def HandleGetCountryList(self):
    """ User wants to create a new account """

    toSend = Packet().create()

    if exists("Data/countryLists/countryList_" + self.CONNOBJ.locale):
        with open("Data/countryLists/countryList_" + self.CONNOBJ.locale) as countryListFile:
            countryListData = countryListFile.readlines()
    else:
        with open("Data/countryLists/default") as countryListFile:
            countryListData = countryListFile.readlines()

    toSend.set("PacketData", "TXN", "GetCountryList")
    toSend.set("PacketData", "countryList.[]", str(len(countryListData)))

    countryId = 0
    for line in countryListData:
        toSend.set("PacketData", "countryList." + str(countryId) + ".ISOCode", line.split("=")[0])
        toSend.set("PacketData", "countryList." + str(countryId) + ".description", line.split("=")[1].replace('"', "").replace("\n", ""))
        countryId += 1

    Packet(toSend).send(self, "acct", 0x80000000, self.CONNOBJ.plasmaPacketID)


def HandleNuGetTos(self):
    """ Get Terms of Use """

    toSend = Packet().create()

    toSend.set("PacketData", "TXN", "GetTos")
    toSend.set("PacketData", "version", "20426_17.20426_17")

    if exists("Data/termsOfUse/termsOfUse_" + self.CONNOBJ.locale):
        with open("Data/termsOfUse/termsOfUse_" + self.CONNOBJ.locale) as termsOfUseFile:
            termsOfUse = termsOfUseFile.read()
    else:
        with open("Data/termsOfUse/default") as termsOfUseFile:
            termsOfUse = termsOfUseFile.read()

    termsOfUse = quote(termsOfUse, safe=" ,.'&/()?;®@§[]").replace("%3A", "%3a").replace("%0A", "%0a") + "%0a%0a%09NFS Carbon Server Emulator by Xan%0aBased on Battlefield%3a Bad Company 2 Master Server Emulator by B1naryKill3r / Tratos%0ahttps://github.com/Tratos/BFBC2_MasterServer"
    toSend.set("PacketData", "tos", termsOfUse)

    Packet(toSend).send(self, "acct", 0x80000000, self.CONNOBJ.plasmaPacketID)


def HandleNuAddAccount(self, data):
    """ Final add account request (with data like email, password...) """

    toSend = Packet().create()
    toSend.set("PacketData", "TXN", "NuAddAccount")

    name = data.get('PacketData', 'name')  # Email
    password = data.get('PacketData', 'password')  # Password

    bd_Day = data.get('PacketData', 'DOBDay')
    bd_Month = data.get('PacketData', 'DOBMonth')
    bd_Year = data.get('PacketData', 'DOBYear')
    birthday = datetime.strptime(bd_Day + " " + bd_Month + " " + bd_Year, "%d %m %Y")
    timeNow = datetime.now()

    country = data.get('PacketData', 'countryCode')

    if len(name) > 32 or len(name) < 3:  # Entered user name length is out of bounds
        toSend.set("PacketData", "errorContainer.[]", "1")
        toSend.set("PacketData", "errorCode", "21")
        toSend.set("PacketData", "localizedMessage", 'The required parameters for this call are missing or invalid')
        toSend.set("PacketData", "errorContainer.0.fieldName", "displayName")

        if len(name) > 32:
            toSend.set("PacketData", "errorContainer.0.fieldError", "3")
            toSend.set("PacketData", "errorContainer.0.value", "TOO_LONG")
            self.logger_err.new_message("[Register] Email " + name + " is too long!", 1)
        else:
            toSend.set("PacketData", "errorContainer.0.fieldError", "2")
            toSend.set("PacketData", "errorContainer.0.value", "TOO_SHORT")
            self.logger_err.new_message("[Register] Email " + name + " is too short!", 1)
    elif db.checkIfEmailTaken(name):  # Email is already taken
        toSend.set("PacketData", "errorContainer.[]", "0")
        toSend.set("PacketData", "errorCode", "160")
        toSend.set("PacketData", "localizedMessage", 'That account name is already taken')
        self.logger_err.new_message("[Register] User with email " + name + " is already registered!", 1)
    elif timeNow.year - birthday.year - ((timeNow.month, timeNow.day) < (birthday.month, birthday.day)) < 18:  # New user is not old enough
        toSend.set("PacketData", "errorContainer.[]", "1")
        toSend.set("PacketData", "errorContainer.0.fieldName", "dob")
        toSend.set("PacketData", "errorContainer.0.fieldError", "15")
        toSend.set("PacketData", "errorCode", "21")
        self.logger_err.new_message("[Register] User with email " + name + " is too young to register new account!", 1)
    elif len(password) > 16:
        toSend.set("PacketData", "errorContainer.[]", "1")
        toSend.set("PacketData", "errorCode", "21")
        toSend.set("PacketData", "localizedMessage", 'The required parameters for this call are missing or invalid')
        toSend.set("PacketData", "errorContainer.0.fieldName", "displayName")
        toSend.set("PacketData", "errorContainer.0.fieldError", "3")
        toSend.set("PacketData", "errorContainer.0.value", "TOO_LONG")
        self.logger_err.new_message("[Register] Password for user " + name + " is too long!", 1)
    elif bool(re.match("^[a-zA-Z0-9]+$", password)) is None:
        toSend.set("PacketData", "errorContainer.[]", "1")
        toSend.set("PacketData", "errorCode", "21")
        toSend.set("PacketData", "localizedMessage", 'The required parameters for this call are missing or invalid')
        toSend.set("PacketData", "errorContainer.0.fieldName", "displayName")
        toSend.set("PacketData", "errorContainer.0.fieldError", "6")
        toSend.set("PacketData", "errorContainer.0.value", "NOT_ALLOWED")
        self.logger_err.new_message("[Register] Password for user " + name + " contains illegal characters!", 1)
    else:
        db.registerUser(name, password, str(birthday).split(" ")[0], country)
        loginData = db.loginUser(name, password)
        self.CONNOBJ.userID = loginData['UserID']
        db.addPersona(self.CONNOBJ.userID, name)
        self.logger.new_message("[Register] User " + name + " was registered successfully!", 1)

    Packet(toSend).send(self, "acct", 0x80000000, self.CONNOBJ.plasmaPacketID)

def CheckUserAlreadyLoggedIn(userID):
	for user in globalUsers:
		if user.UserID == userID:
			return user
	return 0

def HandleNuLogin(self, data):
    """ User is logging in with email and password """

    toSend = Packet().create()
    toSend.set("PacketData", "TXN", "Login")

    returnEncryptedInfo = int(data.get("PacketData", "returnEncryptedInfo"))  # If 1 - User wants to store login information

    try:
        name = data.get('PacketData', "name")
        password = data.get('PacketData', "password")
    except:
        encryptedInfo = data.get("PacketData", "encryptedInfo")

        encryptedLoginData = encryptedInfo.replace("Ciyvab0tregdVsBtboIpeChe4G6uzC1v5_-SIxmvSL", "")
        encryptedLoginData = encryptedLoginData.replace("-", "=").replace("_", "=")  # Bring string into proper format again

        loginData = b64decode(encryptedLoginData).split('\f')

        name = loginData[0]
        password = loginData[1]

    loginData = db.loginUser(name, password)

    if loginData['UserID'] > 0:  # Got UserID - Login Successful
        self.CONNOBJ.accountSessionKey = loginData['SessionID']
        self.CONNOBJ.userID = loginData['UserID']
        self.CONNOBJ.name = name
        #self.CONNOBJ.personaName = name
        useridx = CheckUserAlreadyLoggedIn((int(loginData['UserID'])))
        global globalUserCount
        global globalUsers
        
        if useridx != 0:
            useridx.sessionKey = loginData['SessionID']
        else:
            globalUsers.append(ServerUser())
            globalUsers[globalUserCount].Username = name
            globalUsers[globalUserCount].UserID = int(loginData['UserID'])
            globalUsers[globalUserCount].sessionKey = loginData['SessionID']
            globalUserCount += 1
            
       # print("Session key is:" +globalUsers[0].sessionKey)
        toSend.set("PacketData", "lkey", loginData['SessionID'])
        toSend.set("PacketData", "name", name)

        if returnEncryptedInfo == 1:
            encryptedLoginData = "Ciyvab0tregdVsBtboIpeChe4G6uzC1v5_-SIxmvSL" + b64encode(name + "\f" + password)
            if encryptedLoginData.find('==') != -1:
                encryptedLoginData = encryptedLoginData.replace("==", '-_')
            else:
                encryptedLoginData = encryptedLoginData.replace("=", '-')

            toSend.set("PacketData", "encryptedLoginInfo", encryptedLoginData)

        toSend.set("PacketData", "profileId", str(loginData['UserID']))
        toSend.set("PacketData", "userId", str(loginData['UserID']))

        self.logger.new_message("[Login] User " + name + " logged in successfully!", 1)
    elif loginData['UserID'] == 0:  # The password the user specified is incorrect
        toSend.set("PacketData", "localizedMessage", "The password the user specified is incorrect")
        toSend.set("PacketData", "errorContainer.[]", "0")
        toSend.set("PacketData", "errorCode", "122")

        self.logger_err.new_message("[Login] User " + name + " specified incorrect password!", 1)
    else:  # User not found
        toSend.set("PacketData", "localizedMessage", "The user was not found")
        toSend.set("PacketData", "errorContainer.[]", "0")
        toSend.set("PacketData", "errorCode", "101")

        self.logger_err.new_message("[Login] User " + name + " does not exist", 1)

    personaData = db.loginPersona(self.CONNOBJ.userID, name)
    if personaData is not None:
        self.CONNOBJ.personaID = personaData['personaId']
        self.CONNOBJ.personaSessionKey = personaData['lkey']
        self.CONNOBJ.personaName = name

        self.logger.new_message("[Persona] User " + self.CONNOBJ.name + " just logged as " + name, 1)
    else:
        self.logger_err.new_message("[Persona] User " + self.CONNOBJ.name + " wanted to login as " + name + " but this persona cannot be found!", 1)
    Packet(toSend).send(self, "acct", 0x80000000, self.CONNOBJ.plasmaPacketID)


def HandleNuGetPersonas(self):
    """ Get personas associated with account """

    userID = self.CONNOBJ.userID
    personas = db.getUserPersonas(userID)

    toSend = Packet().create()
    toSend.set("PacketData", "TXN", "NuGetPersonas")
    toSend.set("PacketData", "personas.[]", str(len(personas)))

    personaId = 0
    for persona in personas:
        toSend.set("PacketData", "personas." + str(personaId), persona)
        personaId += 1

    Packet(toSend).send(self, "acct", 0x80000000, self.CONNOBJ.plasmaPacketID)


def HandleNuLoginPersona(self, data):
    """ User logs in with selected Persona """

    toSend = Packet().create()
    toSend.set("PacketData", "TXN", "NuLoginPersona")

    requestedPersonaName = data.get("PacketData", "name")

    personaData = db.loginPersona(self.CONNOBJ.userID, requestedPersonaName)
    if personaData is not None:
        self.CONNOBJ.personaID = personaData['personaId']
        self.CONNOBJ.personaSessionKey = personaData['lkey']
        self.CONNOBJ.personaName = requestedPersonaName

        toSend.set("PacketData", "lkey", personaData['lkey'])
        toSend.set("PacketData", "profileId", str(self.CONNOBJ.personaID))
        toSend.set("PacketData", "userId", str(self.CONNOBJ.personaID))

        self.logger.new_message("[Persona] User " + self.CONNOBJ.name + " just logged as " + requestedPersonaName, 1)
    else:
        toSend.set("PacketData", "localizedMessage", "The user was not found")
        toSend.set("PacketData", "errorContainer.[]", "0")
        toSend.set("PacketData", "errorCode", "101")
        self.logger_err.new_message("[Persona] User " + self.CONNOBJ.name + " wanted to login as " + requestedPersonaName + " but this persona cannot be found!", 1)

    Packet(toSend).send(self, "acct", 0x80000000, self.CONNOBJ.plasmaPacketID)


def HandleNuAddPersona(self, data):
    """ User wants to add a Persona """

    name = data.get("PacketData", "name")

    toSend = Packet().create()
    toSend.set("PacketData", "TXN", "NuAddPersona")

    if len(name) > 16 or len(name) < 3:  # Entered persona name length is out of bounds
        toSend.set("PacketData", "errorContainer.[]", "1")
        toSend.set("PacketData", "errorCode", "21")
        toSend.set("PacketData", "localizedMessage", "The required parameters for this call are missing or invalid")
        toSend.set("PacketData", "errorContainer.0.fieldName", "displayName")

        if len(name) > 16:
            toSend.set("PacketData", "errorContainer.0.fieldError", "3")
            toSend.set("PacketData", "errorContainer.0.value", "TOO_LONG")

            self.logger_err.new_message("[Persona] User " + self.CONNOBJ.name + " wanted to create new persona, but name " + name + " is too long!", 1)
        else:
            toSend.set("PacketData", "errorContainer.0.fieldError", "2")
            toSend.set("PacketData", "errorContainer.0.value", "TOO_SHORT")

            self.logger_err.new_message("[Persona] User " + self.CONNOBJ.name + " wanted to create new persona, but name " + name + " is too short!", 1)
    elif db.getPersonaInfo(name):  # Persona name has to be unique
        toSend.set("PacketData", "errorContainer.[]", "0")
        toSend.set("PacketData", "localizedMessage", "That account name is already taken")
        toSend.set("PacketData", "errorCode", "160")

        self.logger_err.new_message("[Persona] User " + self.CONNOBJ.name + " wanted to create new persona (" + name + "), but persona with this name is already registered in this account!", 1)
    elif bool(re.match("^[a-zA-Z0-9_\-&()*+./:;<=>?\[\]^{|}~]+$", name)) is False:
        toSend.set("PacketData", "errorContainer.[]", "1")
        toSend.set("PacketData", "errorCode", "21")
        toSend.set("PacketData", "localizedMessage", 'The required parameters for this call are missing or invalid')
        toSend.set("PacketData", "errorContainer.0.fieldName", "displayName")
        toSend.set("PacketData", "errorContainer.0.fieldError", "6")
        toSend.set("PacketData", "errorContainer.0.value", "NOT_ALLOWED")
    else:
        db.addPersona(self.CONNOBJ.userID, name)

        self.logger.new_message("[Persona] User " + self.CONNOBJ.name + " just created new persona (" + name + ")", 1)

    Packet(toSend).send(self, "acct", 0x80000000, self.CONNOBJ.plasmaPacketID)


def HandleNuDisablePersona(self, data):
    """ User wants to remove a Persona """

    toSend = Packet().create()
    toSend.set("PacketData", "TXN", "NuDisablePersona")

    personaToDisable = data.get("PacketData", "name")

    if db.getPersonaInfo(personaToDisable):
        db.removePersona(self.CONNOBJ.userID, personaToDisable)

        self.logger.new_message("[Persona] User " + self.CONNOBJ.name + " just removed persona (" + personaToDisable + ")", 1)
    else:
        toSend.set("PacketData", "localizedMessage", "The data necessary for this transaction was not found")
        toSend.set("PacketData", "errorContainer.[]", "0")
        toSend.set("PacketData", "errorCode", "104")
        self.logger_err.new_message("[Persona] User " + self.CONNOBJ.name + " wanted to remove persona (" + personaToDisable + "), but persona with this name didn't exist!", 1)

    Packet(toSend).send(self, "acct", 0x80000000, self.CONNOBJ.plasmaPacketID)


def HandleGetTelemetryToken(self):
    toSend = Packet().create()
    toSend.set("PacketData", "TXN", "GetTelemetryToken")

    tokenbuffer = readFromConfig("connection", "emulator_ip")  # Messenger IP
    tokenbuffer += ","
    tokenbuffer += str(0)  # Messenger Port
    tokenbuffer += ","
    tokenbuffer += ",enUS,^Ů™¨Üś·Ć¤¤‰“ťĘ˙…Ź˛ŃĂÖ¬Ś±ďÄ±ˇ‚†Ś˛°ÄÝ±–†Ě›áî°ˇ‚†Ś°ŕŔ†Ě˛ąĘ‰»¦–Ĺ‚ťŠÔ©Ń©Ż„™’´ČŚ–±äŕł†Ś°îŔáŇĚŰŞÓ€"

    token = b64encode(tokenbuffer).replace("=", "%3d")

    toSend.set("PacketData", "telemetryToken", token)
    toSend.set("PacketData", "enabled", "CA,MX,PR,US,VI,AD,AF,AG,AI,AL,AM,AN,AO,AQ,AR,AS,AW,AX,AZ,BA,BB,BD,BF,BH,BI,BJ,BM,BN,BO,BR,BS,BT,BV,BW,BY,BZ,CC,CD,CF,CG,CI,CK,CL,CM,CN,CO,CR,CU,CV,CX,DJ,DM,DO,DZ,EC,EG,EH,ER,ET,FJ,FK,FM,FO,GA,GD,GE,GF,GG,GH,GI,GL,GM,GN,GP,GQ,GS,GT,GU,GW,GY,HM,HN,HT,ID,IL,IM,IN,IO,IQ,IR,IS,JE,JM,JO,KE,KG,KH,KI,KM,KN,KP,KR,KW,KY,KZ,LA,LB,LC,LI,LK,LR,LS,LY,MA,MC,MD,ME,MG,MH,ML,MM,MN,MO,MP,MQ,MR,MS,MU,MV,MW,MY,MZ,NA,NC,NE,NF,NG,NI,NP,NR,NU,OM,PA,PE,PF,PG,PH,PK,PM,PN,PS,PW,PY,QA,RE,RS,RW,SA,SB,SC,clntSock,SG,SH,SJ,SL,SM,SN,SO,SR,ST,SV,SY,SZ,TC,TD,TF,TG,TH,TJ,TK,TL,TM,TN,TO,TT,TV,TZ,UA,UG,UM,UY,UZ,VA,VC,VE,VG,VN,VU,WF,WS,YE,YT,ZM,ZW,ZZ")
    toSend.set("PacketData", "filters", "")
    toSend.set("PacketData", "disabled", "")

    Packet(toSend).send(self, "acct", 0x80000000, self.CONNOBJ.plasmaPacketID)


def HandleNuGetEntitlements(self, data):
    toSend = Packet().create()
    toSend.set("PacketData", "TXN", "NuGetEntitlements")

    groupName = data.get("PacketData", "groupName")
    userID = self.CONNOBJ.userID

    userEntitlements = db.getUserEntitlements(userID)
    entitlements = []

    for entitlement in userEntitlements:
        if entitlement['groupName'] == groupName:
            entitlements.append(entitlement)

    count = 0
    for entitlement in entitlements:
        toSend.set("PacketData", "entitlements." + str(count) + ".grantDate", entitlement['grantDate'])
        toSend.set("PacketData", "entitlements." + str(count) + ".groupName", entitlement['groupName'])
        toSend.set("PacketData", "entitlements." + str(count) + ".userId", entitlement['userId'])
        toSend.set("PacketData", "entitlements." + str(count) + ".entitlementTag", entitlement['entitlementTag'])
        toSend.set("PacketData", "entitlements." + str(count) + ".version", entitlement['version'])
        toSend.set("PacketData", "entitlements." + str(count) + ".terminationDate", entitlement['terminationDate'])
        toSend.set("PacketData", "entitlements." + str(count) + ".productId", entitlement['productId'])
        toSend.set("PacketData", "entitlements." + str(count) + ".entitlementId", entitlement['entitlementId'])
        toSend.set("PacketData", "entitlements." + str(count) + ".status", entitlement['status'])
        toSend.set("PacketData", "entitlements." + str(count) + ".statusReasonCode", entitlement['statusReasonCode'])
        count += 1

    toSend.set("PacketData", "entitlements.[]", str(len(entitlements)))

    Packet(toSend).send(self, "acct", 0x80000000, self.CONNOBJ.plasmaPacketID)


def HandleNuSearchOwners(self, data):
    toSend = Packet().create()
    toSend.set("PacketData", "TXN", "NuSearchOwners")
    toSend.set("PacketData", "nameSpaceId", "battlefield")

    screenName = data.get("PacketData", "screenName").replace("_", "")
    searchResults = db.searchPersonas(screenName)

    if len(searchResults) != 0:
        count = 0
        for user in searchResults:
            if user['UserID'] != self.CONNOBJ.userID:  # Prevent self-adding
                toSend.set("PacketData", "users." + str(count) + ".id", str(user['PersonaID']))
                toSend.set("PacketData", "users." + str(count) + ".name", user['PersonaName'])
                toSend.set("PacketData", "users." + str(count) + ".type", "1")
                count += 1

        toSend.set("PacketData", "users.[]", str(count))
    else:
        toSend.set("PacketData", "errorContainer.[]", "0")
        toSend.set("PacketData", "errorCode", "104")
        toSend.set("PacketData", "localizedMessage", "The data necessary for this transaction was not found")

    Packet(toSend).send(self, "acct", 0x80000000, self.CONNOBJ.plasmaPacketID)


def HandleGetLockerURL(self):
    toSend = Packet().create()
    toSend.set("PacketData", "TXN", "GetLockerURL")

    url = "http%3a//" + readFromConfig("connection", "emulator_ip") + "/fileupload/locker2.jsp"

    toSend.set("PacketData", "URL", url)

    Packet(toSend).send(self, "acct", 0x80000000, self.CONNOBJ.plasmaPacketID)


def HandleNuLookupUserInfo(self, data):
    toSend = Packet().create()
    toSend.set("PacketData", "TXN", "NuLookupUserInfo")

    personaName = data.get("PacketData", "userInfo.0.userName")
    personaData = db.getPersonaInfo(personaName)

    if personaData is not False:
        toSend.set("PacketData", "userInfo.[]", "1")
        toSend.set("PacketData", "userInfo.0.userName", str(personaData['personaName']))
        toSend.set("PacketData", "userInfo.0.namespace", "battlefield")
        toSend.set("PacketData", "userInfo.0.userId", str(personaData['userID']))
        toSend.set("PacketData", "userInfo.0.masterUserId", str(personaData['personaID']))
    else:
        toSend.set("PacketData", "userInfo.[]", "1")
        toSend.set("PacketData", "userInfo.0.userName", personaName)

    Packet(toSend).send(self, "acct", 0x80000000, self.CONNOBJ.plasmaPacketID)


def ReceivePacket(self, data, txn):
    if txn == 'GetCountryList':
        HandleGetCountryList(self)
    elif txn == 'GetTos':
        HandleNuGetTos(self)
    elif txn == 'AddAccount':
        HandleNuAddAccount(self, data)
    elif txn == 'Login':
        HandleNuLogin(self, data)
    elif txn == 'NuGetPersonas':
        HandleNuGetPersonas(self)
    elif txn == 'NuLoginPersona':
        HandleNuLoginPersona(self, data)
    elif txn == 'NuAddPersona':
        HandleNuAddPersona(self, data)
    elif txn == 'NuDisablePersona':
        HandleNuDisablePersona(self, data)
    elif txn == 'GetTelemetryToken':
        HandleGetTelemetryToken(self)
    elif txn == 'NuGetEntitlements':
        HandleNuGetEntitlements(self, data)
    elif txn == 'NuSearchOwners':
        HandleNuSearchOwners(self, data)
    elif txn == 'GetLockerURL':
        HandleGetLockerURL(self)
    elif txn == 'NuLookupUserInfo':
        HandleNuLookupUserInfo(self, data)
    else:
        self.logger_err.new_message(
            "[" + self.ip + ":" + str(self.port) + ']<-- Got unknown acct message (' + txn + ")", 2)
