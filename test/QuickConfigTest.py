# --- System Libraries ---------------------------------------------------------
import unittest

# --- Project Libraries --------------------------------------------------------
from PacteUtil.QuickConfig import QuickConfig, UserType



class testQuickConfig(unittest.TestCase):

    QuickConfig.config_file_path = "config.properties"

    def testEmptyURL(self):
        loCfg = None
        try:
            loCfg = QuickConfig.configForUser(None, "1", "2", False, 1)
        except Exception as e:
            pass

        self.assertIsNone(loCfg)

        try:
            loCfg = QuickConfig.configForUser("", "1", "2", False, 1)
        except Exception as e:
            pass

        self.assertIsNone(loCfg)

    def testEmptyUser(self):
        loCfg = None
        try:
            loCfg = QuickConfig.configForUser("https://", None, "2", False, 1)
        except Exception as e:
            pass

        self.assertIsNone(loCfg)

        try:
            loCfg = QuickConfig.configForUser("https://", "", "2", False, 1)
        except Exception as e:
            pass

        self.assertIsNone(loCfg)

    def testCredentials(self):
        loCfg = QuickConfig.configForAdminAndUser("https://", "1", "2", "3", "4", "5", "6", False, 1, "")

        self.assertIsNotNone((loCfg.credential.get(UserType.CustomUser)))
        self.assertIsNotNone((loCfg.credential.get(UserType.PacteAdmin)))
        self.assertIsNotNone((loCfg.credential.get(UserType.PSCAdmin)))

        self.assertEqual("1", loCfg.credential.get(UserType.PSCAdmin).username)
        self.assertEqual("2",
                         loCfg.credential.get(UserType.PSCAdmin).password)
        self.assertEqual("3", loCfg.credential.get(UserType.PacteAdmin).username)
        self.assertEqual("4",
                         loCfg.credential.get(UserType.PacteAdmin).password)

        self.assertEqual("5", loCfg.credential.get(UserType.CustomUser).username)
        self.assertEqual("6",
                         loCfg.credential.get(UserType.CustomUser).password)

    def testDefaultAdminConfig(self):
        loCfg = QuickConfig.fromConfigfile()

        self.assertIsNotNone(loCfg.getToken(loCfg.getUserCredential(UserType.PacteAdmin)))
        self.assertIsNotNone(loCfg.getToken(loCfg.getUserCredential(UserType.PSCAdmin)))