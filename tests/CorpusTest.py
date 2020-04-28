# --- System Libraries ---------------------------------------------------------
from pathlib import Path
import unittest
import tempfile
import uuid
import time

# --- Project Libraries --------------------------------------------------------
from PacteClient.CorpusManager import CorpusManager
from PacteUtil.QuickConfig import QuickConfig
from PacteClient.SchemaData import SchemaData, TARGET
from PacteClient.FeatureDefinition import FeatureDefinition
from tests.TestUtil import createTestingUser, createSmallCorpus

QuickConfig.config_file_path = "config.properties"


class TestCorpus(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        createTestingUser()

    def tearDown(self):
        # self.tempdir.cleanup()
        pass

    def testCorpusLifeCycle(self):
        corpus_manager = CorpusManager(QuickConfig.fromConfigfile())
        new_corpus_name = str(uuid.uuid4())

        # Creating new corpus
        print("Creating new corpus... ")
        corpus_id = corpus_manager.createCorpus(new_corpus_name, ["fr-fr"])
        self.assertIsNotNone(corpus_id)
        print("created")

        # Populate
        print("Adding document...")
        doc_id = corpus_manager.addDocument(corpus_id, "bla bla bla", "bla", None, "fr-fr")
        self.assertIsNotNone(doc_id)
        print("Added !")

        # Create annotation group
        print("Creating annotation group...")
        group_id = corpus_manager.createBucket(corpus_id, str(uuid.uuid4()))
        self.assertIsNotNone(group_id)
        print("Created !")

        # Register schema
        print("Generate and add schema...")
        feat_desc = FeatureDefinition("description", "description", "description of description", "", True, ["noop"],
                                      False)
        schemaTest = SchemaData(TARGET.document_surface1d, "TestSchema", {"description": feat_desc})
        schemaId = corpus_manager.registerSchema(schemaTest.to_string())
        print("Created ! (" + schemaId + ")")
        self.assertTrue(corpus_manager.copySchemaToGroup(schemaId, corpus_id, group_id))

        # Remove schema
        print("Deleting schema " + schemaId + " ...")
        corpus_manager.deleteSchema(schemaId)
        print("Schema deleted!")

        # TODO delete annotation group

        # Remove document
        time.sleep(1)
        print("Getting document...")
        self.assertTrue(corpus_manager.getDocument(corpus_id, doc_id).title == "bla")
        print("Document retrieved")

        # Deleting corpus
        print("Deleting corpus...")
        self.assertTrue(corpus_manager.deleteCorpus(corpus_id))
        r = corpus_manager.getcorpus_id(new_corpus_name)
        self.assertIsNone(r)
        print("Deleted !")
        print("Done !")

    def testExportCorpus(self):
        corpus_manager = CorpusManager(QuickConfig.fromConfigfile())

        corpus_id = createSmallCorpus(corpus_manager)

        self.assertIsNotNone(corpus_id)

        print(corpus_id)
        print(corpus_manager.getSize(corpus_id))

        export_completed = corpus_manager.exportToDisk(corpus_id, self.tempdir.name)
        print(export_completed)
        self.assertTrue(export_completed)
        self.assertTrue(len(list(Path(self.tempdir.name).iterdir())) > 0)
        self.assertEqual(2, len(list(Path(self.tempdir.name).joinpath("documents").iterdir())))
