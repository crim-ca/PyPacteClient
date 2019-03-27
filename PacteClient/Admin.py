
# --- Project Libraries --------------------------------------------------------
from PacteUtil.Credential import Credential
from PacteUtil.QuickConfig import UserType


class Admin:

    def __init__(self, toConfig):

        self.cfg = toConfig

    def listAllUsers(self):

        return self.cfg.getRequest(self.cfg.baseURLAuthen + "psc-users-permissions-management/Users/users", UserType.PSCAdmin, None).text

    def resetPassword(self, tsUsername, tsOldPassword, tsNewPassword):
        self.cfg.setCustomUser(tsUsername, tsOldPassword)
        j = dict(password=tsNewPassword)
        resp = self.cfg.putRequest(self.cfg.baseURLAuthen + "/psc-users-permissions-management/Users/myPassword", j,
                                   UserType.CustomUser)

        if resp and len(resp.text) != 0:
            if "id" in resp.json():
                print(resp.text)
                return True

        return False


    def createUser(self, tsUsername, tsPassword, tsPrenom, tsNom):

        loCred = None
        j = dict(password=tsPassword, firstName=tsPrenom, lastName=tsNom,
                 email=tsUsername, jwtAudience=["Pacte"])
        resp = self.cfg.postRequest(self.cfg.baseURLPacteBE + "PlatformUsers/platformUser", UserType.PacteAdmin, j)

        if resp and len(resp.text) > 0 and "userprofileid" in resp.text.lower():
            if self.cfg.verbose:
                print("Utilisateur " + tsUsername + " a été créé !")
                print(resp.text)
            rj = resp.json()
            loCred = Credential(tsUsername, tsPassword,
                                user_id = rj["userId"],
                                user_profile_id=rj["userProfileId"])

        elif self.cfg.verbose:
            if "conflict" in resp.text.lower():
                print("utilisateur " + tsUsername + " existant ! (possiblement avec d'autres accès.")
            elif "unauthorized" in resp.text.lower():
                print("Accès administrateur invalides!")

        return loCred

    def deleteUser(self, tsUserId):
        lsUsername = None

        self.cfg.deleteRequest(self.cfg.baseURLPSCUser + "Users/user/" + tsUserId, UserType.PSCAdmin, None)

        resp = self.cfg.getRequest(self.cfg.baseURLPSCUser + "Users/user/" + tsUserId, UserType.PSCAdmin, None)

        if "username" in resp.json():
            lsUsername = resp.json()["username"]
        elif "not found" in resp.text.lower():
            return True

        return lsUsername == None

    def checkUser(self, tsUsername, tsPassword):
        self.cfg.setCustomUser(tsUsername, tsPassword)
        resp = self.cfg.getRequest(self.cfg.baseURLPacteBE + "PlatformUsers/myPlatformUserContacts",
                            UserType.CustomUser, None)

        if resp and len(resp.text) > 0 and "Forbidden" not in resp.text \
            and "Unauthorized" not in resp.text:
            if self.cfg.verbose:
                print("Utilisateur " + resp.json().get("user").get("userProfileId") + " existant.")

            return resp.json().get("user").get("userProfileId")

        return None

    def addContact(self, tsUserId):

        j = dict(contactUserProfileId=tsUserId)
        resp = self.cfg.postRequest(self.cfg.baseURLPacteBE + "PlatformUsers/myPlatformUserContact", UserType.CustomUser, j)

        if "contactStatus" in resp.json():
            return True
        return False

    def removeContact(self, tsUserId):

        if not tsUserId or len(tsUserId) == 0:
            return False

        resp = self.cfg.deleteRequest(self.cfg.baseURLPacteBE + "PlatformUsers/myPlatformUserContact/" + tsUserId,
                                      UserType.CustomUser, None)

        if not "Unauthorized" in resp.text:
            return True

        return False



