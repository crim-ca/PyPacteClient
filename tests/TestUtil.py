# --- System Libraries ---------------------------------------------------------
from pathlib import Path
import datetime
import time
import json

# --- Project Libraries --------------------------------------------------------
from PacteClient.Admin import Admin
from PacteClient.CorpusManager import CorpusManager
from PacteUtil.QuickConfig import QuickConfig, UserType

SMALL_CORPUS_SIZE = 2
TESTCORPUS = "CorpusTest-999999998"
TRANSCODEGROUP = "Transcode task bucket"


def createSmallCorpus(corpusManager):
    corpusId = corpusManager.getcorpus_id(TESTCORPUS)
    currentTime = datetime.datetime.now().isoformat()
    cptFail = 0
    if corpusId:
        corpusManager.deleteCorpus(corpusId)

        # if corpusManager.getSize(corpusId) == SMALL_CORPUS_SIZE:
        #    return corpusId
    # else:
    #    print("Deleting corrupted small sample corpus...")
    #    corpusManager.deleteCorpus(corpusId)

    # Create the new corpus
    corpusId = corpusManager.createCorpus(TESTCORPUS, ["fr-fr", "en-en"])

    if corpusId:
        transcodeGroup = corpusManager.createBucket(corpusId, TRANSCODEGROUP)
        while not transcodeGroup and cptFail < 10:
            time.sleep(5)
            transcodeGroup = corpusManager.getGroupId(TRANSCODEGROUP, corpusId)
            cptFail += 1

        if not transcodeGroup:
            print("Cannot find transcoder group id")
            return None

        # Register schemas
        try:
            with Path(__file__).parent.parent.joinpath("PacteClient").joinpath("data").joinpath(
                    CorpusManager.DOCMETA).open("r") as docmeta_file:
                transcodeSchema = json.load(docmeta_file)
        except IOError as e:
            print(e)
            return None
        schemaId = corpusManager.getSchemaId(transcodeSchema["schemaType"])
        if not schemaId:
            schemaId = corpusManager.registerSchema(transcodeSchema)
        corpusManager.copySchemaToGroup(schemaId, corpusId, transcodeGroup)

        # Documents and their metadata
        docId = corpusManager.addDocument(corpusId, "bla bla bla", "testExport1", "yep1", "fr-fr")
        time.sleep(5)
        annot = dict(document_size=11, source="tamere.zip", file_edit_date=currentTime,
                     detectedLanguageProb=99.99972436012376,
                     file_type="text/plain; charset=UTF-8",
                     _documentID=docId, file_path="/", indexedLanguage="fr-fr", schemaType="DOCUMENT_META",
                     file_name="1.txt", file_encoding="UTF-8", _corpusID=corpusId, detectedLanguage="fr-fr",
                     file_size=12, file_creation_date=currentTime, file_extension=".txt")

        annotationId = corpusManager.addAnnotation(corpusId, transcodeGroup, annot)

        if not annotationId:
            print("empty annotation 1")

        docId = corpusManager.addDocument(corpusId, "bli bli bli", "testExport2", "yep2", "fr-fr")
        time.sleep(5)
        annot = dict(document_size=11, source="tamere.zip", file_edit_date=currentTime,
                     detectedLanguageProb=99.99972436012376,
                     file_type="text/plain; charset=UTF-8",
                     _documentID=docId, file_path="/", indexedLanguage="fr-fr", schemaType="DOCUMENT_META",
                     file_name="2.txt", file_encoding="UTF-8", _corpusID=corpusId, detectedLanguage="fr-fr",
                     file_size=12, file_creation_date=currentTime, file_extension=".txt")

        annotationId = corpusManager.addAnnotation(corpusId, transcodeGroup, annot)

        if not annotationId:
            print("empty annotation 2")

        # Groups
        corpusManager.createBucket(corpusId, "group1")
        corpusManager.createBucket(corpusId, "group2")
        corpusManager.createBucket(corpusId, "group3");

        # TODO Ajouter schémas et annotations

    return corpusId


def createTestingUser():
    QuickConfig.config_file_path = "config.properties"
    config = QuickConfig.fromConfigfile()
    admin = Admin(config)
    user = config.getUserCredential(UserType.CustomUser)
    userId = admin.checkUser(user.username, user.password)

    if not userId:
        admin.createUser(user.username, user.password, "TestUser", "011")
        userId = admin.checkUser(user.username, user.password)

    return userId is not None
