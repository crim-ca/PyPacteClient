# --- System Libraries ---------------------------------------------------------
import unittest

# --- Project Libraries --------------------------------------------------------
from PacteUtil.QuickConfig import QuickConfig
from PacteClient.FeatureDefinition import FeatureDefinition

QuickConfig.config_file_path = "config.properties"


class TestFeatureDefinition(unittest.TestCase):

    def testJsonToString(self):
        loFD1 = FeatureDefinition("name", "type", "description", "", True, [], True)
        loFD2 = FeatureDefinition.init_from_json("name", loFD1.string_definition())
        self.assertEqual(loFD1.string_definition(), loFD2.string_definition())
