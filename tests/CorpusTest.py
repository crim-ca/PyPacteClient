# --- System Libraries ---------------------------------------------------------
from pathlib import Path
import unittest
import tempfile
import uuid
import time

# --- Project Libraries --------------------------------------------------------
from PacteClient.Admin import Admin
from PacteClient.CorpusManager import CorpusManager
from PacteUtil.QuickConfig import QuickConfig
from tests.TestUtil import createTestingUser, createSmallCorpus


QuickConfig.config_file_path = "config.properties"

class TestCorpus(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        createTestingUser()

    def tearDown(self):
 #       self.tempdir.cleanup()
        pass

    def testCorpusLifeCycle(self):
        corpusManager = CorpusManager(QuickConfig.fromConfigfile())
        newCorpusName = str(uuid.uuid4())

        # Creating new corpus
        print("Creating new corpus... ")
        corpusId = corpusManager.createCorpus(newCorpusName, ["fr-fr"])
        self.assertIsNotNone(corpusId)
        print("created")

        # Populate
        print("Adding document...")
        docId = corpusManager.addDocument(corpusId, "bla bla bla", "bla", None, "fr-fr")
        self.assertIsNotNone(docId)
        print("Added !")

        # Create annotation group
        print("Creating annotation group...")
        groupId = corpusManager.createBucket(corpusId, str(uuid.uuid4()))
        self.assertIsNotNone(groupId)
        print("Created !")

        # TODO delete annotation group

        # Remove document
        time.sleep(1)
        print("Getting document...")
        self.assertTrue(corpusManager.getDocument(corpusId,docId ).title == "bla")
        print("Document retrieved")

        # Deleting corpus
        print("Deleting corpus...")
        self.assertTrue(corpusManager.deleteCorpus(corpusId))
        r = corpusManager.getCorpusId(newCorpusName)
        self.assertIsNone(r)
        print("Deleted !")
        print("Done !")

    def testExportCorpus(self):

        corpusManager = CorpusManager(QuickConfig.fromConfigfile())

        corpusId =  createSmallCorpus(corpusManager)

        self.assertIsNotNone(corpusId)

        print(corpusId)
        print(corpusManager.getSize(corpusId))

        export_completed = corpusManager.exportToDisk(corpusId, self.tempdir.name)
        print(export_completed)
        self.assertTrue(export_completed)
        self.assertTrue(len(list(Path(self.tempdir.name).iterdir()))> 0)
        self.assertEqual(2, len(list(Path(self.tempdir.name).joinpath("documents").iterdir())))








