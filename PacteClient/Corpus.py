# --- System Libraries ---------------------------------------------------------
from collections import defaultdict
from pathlib import Path
import json
import os

# --- Project Libraries --------------------------------------------------------
from PacteUtil.Credential import Credential
from PacteUtil.QuickConfig import UserType


class Corpus:
    CORPUS_STRUCT_FILE = "CorpusStructure.json"
    DOCMETA = "DOCUMENT_META.json"
    DOCMETASchema = "DOCUMENT_META.schema"
    CORPUSMETA = "corpus.json"

    def __init__(self, config):
        self.config = config

    def createCorpus(self, nomCorpus, langList):
        """

        :param nomCorpus:
        :param langList:
        :return:
        """

        idCorpus = None
        j = dict(title=nomCorpus, description="", version="", source="",
                 addAllPermissionsOnTranscoderBucketToOwner=True, reference="",
                 languages=langList)

        resp = self.config.postRequest(self.config.baseURLPacteBE + "Corpora/corpus/",
                                       UserType.CustomUser, j)

        if resp.json().get("id"):
            idCorpus = resp.json().get("id")
            if self.config.verbose:
                print("Corpus {} a été créé !".format(nomCorpus))
        elif resp.json().get("message"):
            print("Cannot create corpus : {}".format(resp.json().get("message")))

        return idCorpus

    def getGroupId(self, bucketName, corpusId):

        groups = self.getGroups(corpusId)
        if groups is not None :
            for group in groups:
                if group["name"] == bucketName:
                    return group["id"]

        return None

    def getGroups(self, corpusId):

        params=dict(includeSchemaJson=False)
        resp = self.config.getRequest(self.config.baseURLPacteBE + "RACSProxy/corpora/"
                               + corpusId + "/structure", UserType.CustomUser,
                               params)

        if resp is not None :
            return  resp.json().get("buckets", None)
        return None

    def getSchemas(self):

        resp = self.config.getRequest(self.config.baseURLPacteBE +
                                      "Schemas/schemas", UserType.CustomUser)

        if resp is not None :
            return  resp.json()
        return None

    def getSchema(self, schemaId):

        resp = self.config.getRequest(self.config.baseURLPacteBE + "Schemas/schema/" + schemaId,
                                      UserType.CustomUser)

        if resp :
            return resp.json()

        return None


    def createBucket(self, corpusId, bucketName):

        j = dict(id=corpusId, name=bucketName)

        resp = self.config.postRequest(self.config.baseURLPacteBE +
                                       "Corpora/corpusBucket/" + corpusId,
                                       UserType.CustomUser, j)

        if resp is not None :
            return resp.json().get("bucketId", None)

        return None

    def getSchemaId(self, schemaName, corpusId=None, bucketId=None):
        schemaList = self.getSchemas()

        for schema in schemaList:
            if schema["schema"]["schemaType"].lower() == schemaName.lower():
                schemaId = schema["schema"]["id"]
                corpus_list = schema["relatedCorpusBuckets"]

                if (not corpusId or len(corpusId) == 0) \
                        and (not bucketId or len(bucketId) == 0)\
                        and len(corpus_list) == 0:
                    return schemaId
                elif ((bucketId and len(bucketId) > 0)
                    or corpusId and len(corpusId) > 0 ) and  len(corpus_list) > 0:
                    corp =  corpus_list[0]["corpusId"]
                    buck = corpus_list[0]["bucketId"]

                    if len(corp) == 0 or (corp == corpusId and (len(buck) == 0 or buck == bucketId)):
                        return schemaId

        return None

    def registerSchema(self, schema_json):

        j= dict(schemaJsonContent=schema_json)

        resp =  self.config.postRequest(self.config.baseURLPacteBE + "Schemas/schema",
                                        UserType.CustomUser, j)

        if resp :
            return resp.json().get("id", None)

        return None

    def copySchemaToGroup(self, schemaId, corpusId, bucketId):

        j = dict(corpusId=corpusId, bucketId=bucketId)

        self.config.putRequest(self.config.baseURLPacteBE + "Schemas/schemaToCorpusBucket/" + schemaId,
                               UserType.CustomUser, j)

        return True

    def addDocument(self, corpusId, content, title, source, language):

        j = dict(title=title, source=source, text=content, language=language)

        resp = self.config.postRequest(self.config.baseURLPacteBE + "RACSProxy/corpora/" + corpusId + "/documents",
                                       UserType.CustomUser, j)

        if resp:
            return resp.json.get("id", None)
        else:
            print(resp)

        return None

    def addAnnotation(self, corpusId, groupId, annotation):

        resp = \
            self.config.postRequest(
                self.config.baseURLPacteBE + "RACSProxy/corpora/" + corpusId +
                "/buckets/" + groupId + "/annotations",
            UserType.CustomUser, annotation)

        if resp :
            id = resp.json().get("id", None)
            if id is None:
                print(resp)
            return id
        else:
            return None

    def getCorpusMetadata(self, corpusId):

        return self.config.getRequest(self.config.baseURLPacteBE + "Corpora/corpus/" + corpusId, UserType.CustomUser)

    def importCorpus(self, corpus_dir):

        groups_dict = dict()

        corpus_dir_path = Path(corpus_dir)
        if not corpus_dir_path.exists():
            return None
        try:
            with corpus_dir_path.joinpath(Corpus.CORPUSMETA).open("r") as corpus_meta_file:
                corpus_meta = json.load(corpus_meta_file)
        except IOError:
            print("Missing corpus metadata")
            return None

        corpusOldId = corpus_meta["id"]
        corpusNewId = self.createCorpus(corpus_meta["title"] + " - Import", corpus_meta["languages"])

        # TODO: timeout ?

        try:
            with corpus_dir_path.joinpath(Corpus.CORPUS_STRUCT_FILE).open(
                    "r") as corpus_meta_file:
                corpus_struct = json.load(corpus_meta_file)
        except IOError:
            print("Corpus structure is missing from exporte")
            return None


        # Création des groupes
        groups = corpus_struct["buckets"]

        for group in groups :
            oldGroupId = group["id"]
            groupId =  self.getGroupId(group["name"], corpusNewId)
            if groupId is None:
                groupId = self.createBucket(corpusNewId, group["name"])
            groups_dict[oldGroupId] = groupId

            # Ajout des schémas disponibles
            schemas = group["schemas"]
            for schema in schemas:
                schema_file_path = corpus_dir_path.joinpath("groups")\
                    .joinpath(oldGroupId).joinpath(schema["schemaType"]).with_suffix(".schema")
                if schema_file_path.exists():
                    with schema_file_path.open("r") as schema_file:
                        schema_j = json.load(schema_file)["schema"]["schemaJsonContent"]
                elif schema_file_path.name.lower() == Corpus.DOCMETASchema.lower():
                    try:
                        with Path(__file__).joinpath("data").joinpath(Corpus.DOCMETASchema).open("r") as docmeta_file:
                            schema_j = json.load(docmeta_file)
                    except IOError as e:
                        print(e)
                schemaId = self.getSchemaId(schema_j["schemaType"])
                if schemaId is None:
                    schemaId = self.registerSchema(schema_j)
                self.copySchemaToGroup(schemaId, corpusNewId, groupId)


        # Uploader les documents
        document_dir_path = corpus_dir_path.joinpath("documents")

        try:
            for p in document_dir_path.iterdir():
                with p.open("r") as doc_f:
                    doc_json =  json.load(doc_f)
                docOldId = doc_json["id"]
                docId = self.addDocument(corpusNewId, doc_json["text"], doc_json["title"], doc_json["source"], doc_json["language"])

                # Ajouter les annotations
                for old_group_id, new_group_id in groups_dict.items():
                    annot_file_path = corpus_dir_path.joinpath(groups).joinpath(old_group_id).joinpath(docOldId).with_suffix(".json")
                    if not annot_file_path.exists():
                        continue
                    with annot_file_path.open("r") as annot_file:
                        annot = json.load(annot_file)
                    if annot is None :
                        continue
                    elif type(annot) == dict:
                        annot = annot[corpusOldId][groupId]

                    for a in annot:
                        del(a["annotationId"])
                        a["_corpusId"] = corpusNewId
                        a["_documentID"] = docId

                        if "domainName" in a:
                            a["domainName"] = a["domainName"].replace(" ", "")

                        if "domainScore" in a :
                            if  a["domainScore"] >= 0.0001:
                                self.addAnnotation(corpusNewId, new_group_id, a)
                        else:
                            self.addAnnotation(corpusNewId, new_group_id, a)
        except IOError as e:
            print("Corpus upload failed : " + str(e))
            return None

        return corpusNewId


    def exportToDisk(self, corpusId, outputDir, exportGroupIdList=None):

        buckets = defaultdict(list)
        outputPath= Path(outputDir)

        if not outputPath.exists():
            return False

        # Prepare the subfolders
        docFolderPath = outputPath.joinpath("documents")
        groupFolderPath = outputPath.joinpath("groups")

        docFolderPath.mkdir()
        groupFolderPath.mkdir()

        # Download corpus specs and save them
        with outputPath.joinpath("corpus.json").open("w") as corpus_file:
            json.dump(self.getCorpusMetadata(corpusId).json(), corpus_file, indent=4)

        # Download the corpus structure and replicate it
        resp = self.config.getRequest(self.config.baseURLPacteBE + "RACSProxy/corpora/" + corpusId + "/structure",
                                      UserType.CustomUser)

        if resp:
            j = resp.json()
            with outputPath.joinpath(Corpus.CORPUS_STRUCT_FILE).open("w") as struct_file:
                json.dump(j, struct_file, indent=4)

            for b in j.get("buckets", None):
                bucket_id = b["id"]
                if exportGroupIdList is None or bucket_id in exportGroupIdList:
                    groupPath = groupFolderPath.joinpath(bucket_id)
                    groupPath.mkdir()
                    for schema in  b["schemas"]:
                        schemaName =  schema["schemaType"]
                        buckets[bucket_id].append(schemaName)
                        schemaId = self.getSchemaId(schemaName, corpusId, bucket_id)
                        if schemaId :
                            with groupFolderPath.joinpath(schemaName).with_suffix(".schema").open(
                                    "w") as schema_file:
                                json.dump(self.getSchema(schemaId), schema_file, indent=4)


            # Check if all required groups are in the structure, if not, exit.









