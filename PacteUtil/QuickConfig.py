# --- System Libraries ---------------------------------------------------------
import enum
import datetime
import configparser

# --- 3rd party Libraries ------------------------------------------------------
import requests
import validators

# --- Project Libraries --------------------------------------------------------
from PacteUtil.Credential import Credential


class UserType(enum.Enum):
    PSCAdmin = 1
    PacteAdmin = 2
    CustomUser = 3


class QuickConfig:
    # httpClient = requests.session()
    config_file_path = "config.properties"

    @staticmethod
    def readConfiguration(config_file_path, config="STAGING"):
        cfg = configparser.ConfigParser()

        try:
            with open(config_file_path) as cfp:
                cfg.read_file(cfp)
        except IOError as ioe:
            print("IO error: {}".format(ioe))

        return cfg._sections[config]

    @classmethod
    def fromConfigfile(cls):
        cfg_dict = QuickConfig.readConfiguration(QuickConfig.config_file_path)

        tsBaseURLAuthen = cfg_dict["server"]
        tsBaseURLService = cfg_dict["serviceurl"]

        tniTokenRenewDelay = int(cfg_dict["tokenrenewdelay"])
        tbVerbose = cfg_dict["verbose"] in ["true", "True"]
        tsAdminPSCUsername = cfg_dict.get("pscadmin", None)
        tsAdminPSCPassword = cfg_dict.get("pscadminpwd", None)
        tsAdminPacteUsername = cfg_dict.get("pacteadmin", None)
        tsAdminPactePassword = cfg_dict.get("pacteadminpwd", None)
        tsCustomUser = cfg_dict.get("standarduser", None)
        tsCustomPassword = cfg_dict.get("standarduserpwd", None)
        cfg = cls()

        cfg.setConfig(tsBaseURLAuthen, tsBaseURLService, tniTokenRenewDelay,
                      tbVerbose, tsAdminPSCUsername, tsAdminPSCPassword,
                      tsAdminPacteUsername, tsAdminPactePassword, tsCustomUser,
                      tsCustomPassword)

        return cfg

    # New configuration with admin and user level credentials
    @classmethod
    def configForAdminAndUser(cls, tsBasePacteUrl, tsAdminPSCUsername, tsAdminPSCPassword,
                              tsAdminPacteUsername, tsAdminPactePassword, tsCustomUser, tsCustomPassword,
                              tbVerbose, tniTokenRenewDelay, tsServiceUrl):
        if not tsBasePacteUrl or len(tsBasePacteUrl) == 0:
            raise ValueError("PACTE url should not be null")

        cfg = cls()

        cfg.setConfig(tsBasePacteUrl, tsServiceUrl, tniTokenRenewDelay,
                      tbVerbose, tsAdminPSCUsername, tsAdminPSCPassword,
                      tsAdminPacteUsername, tsAdminPactePassword, tsCustomUser,
                      tsCustomPassword)
        return cfg

    # New configuration with user level credentials
    @classmethod
    def configForUser(cls, tsBasePacteUrl, tsCustomUser, tsCustomPassword,
                      tbVerbose=False, tniTokenRenewDelay=1):
        if not tsBasePacteUrl or len(tsBasePacteUrl) == 0:
            raise ValueError("PACTE url should not be null")

        if not tsCustomUser or len(tsCustomUser) == 0:
            raise ValueError("Username should not be null")

        cfg = cls()
        cfg_dict = QuickConfig.readConfiguration(QuickConfig.config_file_path)
        tsBaseURLService = cfg_dict["serviceurl"]

        cfg.setConfig(tsBasePacteUrl, tsBaseURLService, tniTokenRenewDelay,
                      tbVerbose, None, None, None, None, tsCustomUser, tsCustomPassword)
        return cfg

    def __init__(self, tsBaseURLAuthen="", tsBaseURLPacteBE="", tsBaseURLPSCUser="", tsBaseURLService="",
                 tniTokenRenewDelay=-12, tpVerbose=True, toCredential: Credential = None):

        self.baseURLAuthen = tsBaseURLAuthen
        self.baseURLPacteBE = tsBaseURLPacteBE
        self.baseURLPSCUser = tsBaseURLPSCUser
        self.baseURLService = tsBaseURLService
        self.tokenRenewDelay = tniTokenRenewDelay
        self.verbose = tpVerbose
        if toCredential:
            self.credential = toCredential
        else:
            self.credential = dict()

    def setConfig(self, tsBaseURLAuthen, tsBaseURLService, tniTokenRenewDelay,
                  tbVerbose, tsAdminPSCUsername, tsAdminPSCPassword,
                  tsAdminPacteUsername, tsAdminPactePassword, tsCustomUser,
                  tsCustomPassword):

        self.baseURLAuthen = tsBaseURLAuthen
        if not self.baseURLAuthen.endswith("/"):
            self.baseURLAuthen += "/"

        self.baseURLPacteBE = self.baseURLAuthen + "pacte-backend/"
        self.baseURLPSCUser = self.baseURLAuthen + "psc-users-permissions-management/"
        self.baseURLService = tsBaseURLService
        if not self.baseURLService.endswith("/"):
            self.baseURLService += "/"

        self.tokenRenewDelay = tniTokenRenewDelay
        self.verbose = tbVerbose

        # PSC Admin
        if tsAdminPSCUsername and tsAdminPSCPassword:
            self.credential[UserType.PSCAdmin] = \
                Credential(tsAdminPSCUsername, tsAdminPSCPassword)

        # Pacte Admin
        if tsAdminPacteUsername and tsAdminPactePassword:
            self.credential[UserType.PacteAdmin] = \
                Credential(tsAdminPacteUsername, tsAdminPactePassword)

        # Pacte Custom User
        if tsCustomUser and tsCustomPassword:
            self.credential[UserType.CustomUser] = \
                Credential(tsCustomUser, tsCustomPassword)

    def setCustomUser(self, username: str, password: str):
        self.credential[UserType.CustomUser] = \
            Credential(username, password)

    def getUserCredential(self, user_type: UserType):
        return self.credential.get(user_type, None)

    def setAuthenUrl(self, url: str):
        self.baseURLAuthen = url
        if not url.endswith("/"):
            self.baseURLAuthen += "/"

    def setServiceUrl(self, service_url: str):
        self.baseURLService = service_url
        if not service_url.endswith("/"):
            self.baseURLService += "/"

    def getToken(self, user_credentials: Credential):
        ret = ""

        time_limit = datetime.datetime.now() - datetime.timedelta(hours=self.tokenRenewDelay)
        if user_credentials.tokenCreation is None or (user_credentials.tokenCreation < time_limit):
            user_credentials.setToken(None)

            json_dict = {"username": user_credentials.username,
                         "password": user_credentials.password,
                         "jwtAudience": ["Pacte"]}

            ret = requests.post(self.baseURLAuthen + "psc-authentication-service/FormLogin/login",
                                json=json_dict)

        if ret and len(ret.text) > 0 and "unauthorized" not in ret.text:
            user_credentials.setToken(ret.json().get("token"))

        return user_credentials.token

    def getRequest(self, target_endpoint: str, user_type: UserType, toParams=None):
        resp = None

        try:
            validators.url(target_endpoint)
        except validators.ValidationFailure as val:
            if (self.verbose):
                print(val)
            return None

        if user_type:
            headers = {"Authorization": "Bearer " + str(self.getToken(self.credential.get(user_type))),
                       "AuthorizationAudience": "Pacte"}
        else:
            headers = None

        try:
            resp = requests.get(target_endpoint, params=toParams, headers=headers)
            if self.verbose or (resp.status_code != 200 and resp.status_code != 204):
                print("Response Status : " + str(resp.status_code))

        except Exception as e:
            print(e)

        return resp

    def deleteRequest(self, target_endpoint: str, user_type: UserType, toParams=None):
        resp = None

        try:
            validators.url(target_endpoint)
        except validators.ValidationFailure as val:
            if (self.verbose):
                print(val)
            return None

        if user_type:
            headers = {"Authorization": "Bearer " + self.getToken(
                self.credential.get(user_type)),
                       "AuthorizationAudience": "Pacte"}
        else:
            headers = None

        try:
            resp = requests.delete(target_endpoint, params=toParams, headers=headers)
            if self.verbose or (resp.status_code != 200 and resp.status_code != 204):
                print("Response Status : " + str(resp.status_code))

        except Exception as e:
            print(e)

        return resp

    def postRequest(self, target_endpoint: str, user_type: UserType, tdJson2Post, filedata=None):
        resp = None

        try:
            validators.url(target_endpoint)
        except validators.ValidationFailure as val:
            if self.verbose:
                print(val)
            return None

        if user_type:
            headers = {"Authorization": "Bearer " + self.getToken(
                self.credential.get(user_type)),
                       "AuthorizationAudience": "Pacte"}
        else:
            headers = dict()

        if not filedata:
            headers["Content-type"] = "application/json"
            headers["Accept"] = "application/json"

        try:
            if filedata:
                resp = requests.post(target_endpoint, headers=headers, data=tdJson2Post, files=filedata)
            else:
                resp = requests.post(target_endpoint, json=tdJson2Post, headers=headers)

            if self.verbose or (resp.status_code != 200 and resp.status_code != 204):
                print("Response Status : " + str(resp.status_code))
                print(resp.text)

        except Exception as e:
            print(e)

        return resp

    def putRequest(self, target_endpoint: str, user_type: UserType, tdJson2Put):
        resp = None

        try:
            validators.url(target_endpoint)
        except validators.ValidationFailure as val:
            if self.verbose:
                print(val)
            return None

        if user_type:
            headers = {"Authorization": "Bearer " + self.getToken(
                self.credential.get(user_type)),
                       "AuthorizationAudience": "Pacte"}
        else:
            headers = dict()

        headers["Content-type"] = "application/json"
        headers["Accept"] = "application/json"
        try:
            resp = requests.put(target_endpoint, json=tdJson2Put,
                                headers=headers)

            if self.verbose or (
                    resp.status_code != 200 and resp.status_code != 204):
                print("Response Status : " + str(resp.status_code))

        except Exception as e:
            print(e)

        return resp
