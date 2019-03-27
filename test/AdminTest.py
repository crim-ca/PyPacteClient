# --- System Libraries ---------------------------------------------------------
import unittest
import uuid

# --- Project Libraries --------------------------------------------------------
from PacteClient.Admin import Admin
from PacteUtil.Credential import Credential
from PacteUtil.QuickConfig import QuickConfig



class testAdmin(unittest.TestCase):

    QuickConfig.config_file_path = "config.properties"

    def setUp(self):

        username1 = "testuser-unlinked1@test.com"
        pswd1 = "secret"
        username2 = "testuser-unlinked2@test.com"
        pswd2 = "secret"

        admin = Admin(QuickConfig.fromConfigfile())
        id1 = admin.checkUser(username1, pswd1)
        id2 = admin.checkUser(username2, pswd2)

        if not id1:
            admin.createUser(username1, pswd1,"testingUser1", "testingUser1")

        if not id2:
            admin.createUser(username2, pswd2,"testingUser2", "testingUser2")

    def testLinkUsers(self):

        username1 = str(uuid.uuid4())
        password1 = str(uuid.uuid4())
        username2 = str(uuid.uuid4())
        password2 = str(uuid.uuid4())

        cfg = QuickConfig.fromConfigfile()
        admin = Admin(cfg)

        user1 = admin.createUser(username1, password1, str(uuid.uuid4()), str(uuid.uuid4()))
        user2 = admin.createUser(username2, password2, str(uuid.uuid4()),
                               str(uuid.uuid4()))

        cfg.setCustomUser(username1, password1)
        admin.removeContact(user2.userProfileId)
        self.assertTrue(admin.addContact(user2.userProfileId))
        self.assertTrue(admin.removeContact(user2.userProfileId))

        admin.deleteUser(user1.userId)
        self.assertIsNone(admin.checkUser(username1, password1))

        cfg.setCustomUser(username2, password2)
        admin.deleteUser(user2.userId)
        self.assertIsNone(admin.checkUser(username2, password2))

