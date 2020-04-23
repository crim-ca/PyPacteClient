# --- System Libraries ---------------------------------------------------------
from collections import defaultdict
from pathlib import Path
import json
import sys
import os

# --- Project Libraries --------------------------------------------------------
from PacteUtil.QuickConfig import QuickConfig, UserType
from PacteClient.PacteDocument import PacteDocument


class CorpusManager:
    CORPUS_STRUCT_FILE = "CorpusStructure.json"
    DOCMETA = "DOCUMENT_META.json"
    DOCMETASchema = "DOCUMENT_META.schema"
    CORPUSMETA = "corpus.json"

    def __init__(self, config: QuickConfig):
        self.config: QuickConfig = config

    def createCorpus(self, corpus_name: str, langs: list):
        """
        Create an empty corpus on the platform
        :param corpus_name:
        :param langs: List of the two-letter language code that the corpus will contain
        :return:
        """

        idCorpus = None
        j = dict(title=corpus_name, description="", version="", source="",
                 addAllPermissionsOnTranscoderBucketToOwner=True, reference="",
                 languages=langs)

        resp = self.config.postRequest(self.config.baseURLPacteBE + "Corpora/corpus",
                                       UserType.CustomUser, j)

        if resp.json().get("id"):
            idCorpus = resp.json().get("id")
            if self.config.verbose:
                print("Corpus {} a été créé !".format(corpus_name))
        elif resp.json().get("message"):
            print("Cannot create corpus : {}".format(resp.json().get("message")))

        return idCorpus

    def injectCorpus(self, corpus_id: str, zipfile, options):
        '''
        Upload a zip file containing documents to be transcoded into a specific corpus
        :param corpus_id: unique identification code of the corpusUnique id of the targeted corpus
        :param zipfile: The zip file to upload in the corpus
        :param options: Filtering options for the transcoding and import operation
        :return: If the operation started with success
        '''

        if corpus_id is None or len(corpus_id) == 0:
            return False

        j2p = {"corpus_id": corpus_id,
               "options": options}
        form_data = {"file": (os.path.basename(zipfile), open(zipfile, 'rb', encoding="UTF-8"))}

        resp = self.config.postRequest(self.config.baseURLPacteBE + "Corpora/importCorpusDocuments",
                                       UserType.CustomUser, j2p, multipartdata=form_data)

        if resp and len(resp.text) == 0:
            return True
        else:
            return False

    def deleteCorpus(self, corpus_id: str):
        if corpus_id is None or len(corpus_id) == 0:
            return False

        resp = self.config.deleteRequest(self.config.baseURLPacteBE + "Corpora/corpus/" + corpus_id,
                                         UserType.CustomUser)
        if resp and len(resp.text) == 0:
            return True

        return False

    def getSize(self, corpus_id: str):
        #  String lsResponse = null;
        #         lsResponse = poCfg.getRequest(poCfg.getPacteBackend() + "Corpora/corpus/" + tscorpus_id, USERTYPE.CustomUser,
        #                 null);
        #
        #         if (lsResponse != null && !lsResponse.isEmpty()) {
        #             JSONObject loJson = new JSONObject(lsResponse);
        #             if (loJson.has("documentCount"))
        #                 return loJson.getInt("documentCount");
        #             else
        #                 System.err.println("No document count returned : " + lsResponse);
        #         }
        #
        #         return null;
        resp = self.config.getRequest(self.config.baseURLPacteBE + "Corpora/corpus/" + corpus_id,
                                      UserType.CustomUser)

        if resp and len(resp.text) > 0:
            j = resp.json()
            if "documentCount" in j:
                return j["documentCount"]
            else:
                print("No document count returned : " + resp.text)

        return None

    def createTagset(self, tagset_definition: str):
        """
        Add a new tagset in the user space.
        :param tagset_definition:
        :return:
        """
        j = dict(tagsetJsonContent=tagset_definition)
        resp = self.config.postRequest(self.config.baseURLPacteBE + "Tagsets/tagset", UserType.CustomUser, j)
        if resp and resp.json().get("id", None):
            return resp.json().get("id")
        return None

    def deleteTagset(self, tagset_id: str):
        """
        Remove a tagset from the user space.
        :param tagset_id:
        :return:
        """
        if tagset_id is None or len(tagset_id) == 0:
            return False

        resp = self.config.deleteRequest(self.config.baseURLPacteBE + "Tagsets/tagset/" + tagset_id,
                                         UserType.CustomUser)
        if resp and len(resp.text) == 0:
            return True

        return False

    def getTagset(self, tagset_id: str):
        """
        Return the required tagset definition
        :param tagset_id: Unique identification of the tagset
        :return: The json string definition of the tagset if found, None if not.
        """
        resp = self.config.getRequest(self.config.baseURLPacteBE + "Tagsets/tagset/" + tagset_id,
                                      UserType.CustomUser)
        if resp and len(resp.text) > 0:
            return resp.json()

        return None

    def getTagsetId(self, tagset_name: str):
        """
        Get the first unique identifier of a tagset from a name
        :param tagset_name:
        :return: The id of the first tagset with the desired name, None if not found.
        """
        resp = self.config.getRequest(self.config.baseURLPacteBE + "Tagsets/tagsets", UserType.CustomUser)
        if resp:
            tagset_list = resp.json()

            for tagset in tagset_list:
                if tagset.get("tagsetJsonContent", dict()).get("title", "").lower() == tagset_name.lower():
                    return tagset["id"]

        return None

    def getGroupId(self, bucket_name: str, corpus_id: str):
        """

        :param bucket_name:
        :param corpus_id:
        :return:
        """
        groups = self.getGroups(corpus_id)
        if groups is not None:
            for group in groups:
                if group["name"] == bucket_name:
                    return group["id"]

        return None

    def getGroups(self, corpus_id: str):

        params = dict(includeSchemaJson=False)
        resp = self.config.getRequest(self.config.baseURLPacteBE + "RACSProxy/corpora/"
                                      + corpus_id + "/structure", UserType.CustomUser,
                                      params)

        if resp is not None:
            return resp.json().get("buckets", None)
        return None

    def getSchemas(self):

        resp = self.config.getRequest(self.config.baseURLPacteBE +
                                      "Schemas/schemas", UserType.CustomUser)

        if resp is not None:
            return resp.json()
        return None

    def getSchema(self, schema_id: str):

        resp = self.config.getRequest(self.config.baseURLPacteBE + "Schemas/schema/" + schema_id,
                                      UserType.CustomUser)

        if resp:
            return resp.json()

        return None

    def deleteSchema(self, schema_id: str):
        self.config.deleteRequest(self.config.baseURLPacteBE + "Schemas/schema/" + schema_id,
                                  UserType.CustomUser)

        return True

    def createBucket(self, corpus_id, bucketName):

        j = dict(id=corpus_id, name=bucketName)

        resp = self.config.postRequest(self.config.baseURLPacteBE +
                                       "Corpora/corpusBucket/" + corpus_id,
                                       UserType.CustomUser, j)

        if resp is not None:
            return resp.json().get("bucketId", None)

        return None

    def getSchemaId(self, schemaName, corpus_id=None, bucketId=None):
        schemaList = self.getSchemas()

        for schema in schemaList:
            if schema["schema"]["schemaType"].lower() == schemaName.lower():
                schemaId = schema["schema"]["id"]
                corpus_list = schema["relatedCorpusBuckets"]

                if (not corpus_id or len(corpus_id) == 0) \
                        and (not bucketId or len(bucketId) == 0) \
                        and len(corpus_list) == 0:
                    return schemaId
                elif ((bucketId and len(bucketId) > 0)
                      or corpus_id and len(corpus_id) > 0) and len(corpus_list) > 0:
                    corp = corpus_list[0]["corpus_id"]
                    buck = corpus_list[0]["bucketId"]

                    if len(corp) == 0 or (corp == corpus_id and (len(buck) == 0 or buck == bucketId)):
                        return schemaId

        return None

    def registerSchema(self, schema_json):

        j = dict(schemaJsonContent=schema_json)

        resp = self.config.postRequest(self.config.baseURLPacteBE + "Schemas/schema",
                                       UserType.CustomUser, j)

        if resp:
            return resp.json().get("id", None)

        return None

    def copySchemaToGroup(self, schemaId, corpus_id, bucketId):

        j = dict(corpus_id=corpus_id, bucketId=bucketId)

        self.config.putRequest(self.config.baseURLPacteBE + "Schemas/schemaToCorpusBucket/" + schemaId,
                               UserType.CustomUser, j)

        return True

    def addDocument(self, corpus_id, content, title, source, language):

        j = dict(title=title, source=source, text=content, language=language)

        resp = self.config.postRequest(self.config.baseURLPacteBE + "RACSProxy/corpora/" + corpus_id + "/documents",
                                       UserType.CustomUser, j)

        if resp:
            return resp.json().get("id", None)
        else:
            print(resp)

        return None

    def addAnnotation(self, corpus_id, groupId, annotation):

        resp = \
            self.config.postRequest(
                self.config.baseURLPacteBE + "RACSProxy/corpora/" + corpus_id +
                "/buckets/" + groupId + "/annotations",
                UserType.CustomUser, annotation)

        if resp:
            id = resp.json().get("id", None)
            if id is None:
                print(resp)
            return id
        else:
            return None

    def getCorpusMetadata(self, corpus_id):

        return self.config.getRequest(self.config.baseURLPacteBE + "Corpora/corpus/" + corpus_id, UserType.CustomUser)

    def getcorpus_id(self, corpusName):
        resp = self.config.getRequest(self.config.baseURLPacteBE + "Corpora/corpora", UserType.CustomUser)
        if resp and len(resp.text) > 0:
            corpora_list = resp.json()
            for corpus in corpora_list:
                if corpus.get("title", None) and corpus.get("title").lower() == corpusName.lower():
                    return corpus.get("id")

        return None

    def getDocument(self, corpus_id, documentId):

        resp = self.config.getRequest(self.config.baseURLPacteBE + "RACSProxy/corpora/" + corpus_id
                                      + "/documents/" + documentId, UserType.CustomUser)

        if resp and len(resp.text) > 0:
            j = resp.json()

            return PacteDocument(documentId, j["title"], j["text"], j["source"], j["language"])

        return None

    def getDocuments(self, corpus_id):
        """
        Get the list of all the documents in a corpus
        :param corpus_id: unique identification code of the corpusunique identification code of the corpus
        :return: 
        """
        if corpus_id is None or len(corpus_id.strip()) == 0:
            return None
        docs = []
        nbPages = 0
        params = dict(entriesperpage=2)
        maxDocs = sys.maxsize
        while len(docs) < maxDocs:
            nbPages += 1
            params["page"] = nbPages
            resp = self.config.getRequest(self.config.baseURLPacteBE + "Corpora/documentsCorpus/" + corpus_id,
                                          UserType.CustomUser, toParams=params)
            if resp is None or len(resp.json()["documents"]) == 0:
                return docs
            j = resp.json()
            maxDocs = j["documentCount"]
            new_docs = j["documents"]
            for doc in new_docs:
                docs.append(PacteDocument(doc["id"], doc["title"], None, None, doc["language"], doc["docByteSize"],
                                          doc["dateAdded"], doc["path"]))
        return docs

    def getAnnotations(self, corpus_id, docId, schemaTypes):
        params = dict(schemaTypes=schemaTypes)
        return self.config.getRequest(self.config.baseURLPacteBE + "RACSProxy/annosearch/corpora/" +
                                      corpus_id + "/documents/" + docId, UserType.CustomUser, toParams=params).json()

    def copyAnnotationGroup(self, corpus_id: str, group_src_id: str, group_dest_id: str):
        """
        Copy the schemas and annotations from one group to another in the same corpus
        :param corpus_id: unique identification code of the corpus
        :param group_dest_id: 
        :param group_src_id:        
        :return: 
        """
        raise NotImplemented

    def importCorpus(self, corpus_dir):

        groups_dict = dict()

        corpus_dir_path = Path(corpus_dir)
        if not corpus_dir_path.exists():
            return None
        try:
            with corpus_dir_path.joinpath(CorpusManager.CORPUSMETA).open("r", encoding="UTF-8") as corpus_meta_file:
                corpus_meta = json.load(corpus_meta_file)
        except IOError:
            print("Missing corpus metadata")
            return None

        corpusOldId = corpus_meta["id"]
        corpusNewId = self.createCorpus(corpus_meta["title"] + " - Import", corpus_meta["languages"])

        # TODO: timeout ?

        try:
            with corpus_dir_path.joinpath(CorpusManager.CORPUS_STRUCT_FILE).open(
                    "r", encoding="UTF-8") as corpus_meta_file:
                corpus_struct = json.load(corpus_meta_file)
        except IOError:
            print("Corpus structure is missing from exporte")
            return None

        # Création des groupes
        groups = corpus_struct["buckets"]

        for group in groups:
            oldGroupId = group["id"]
            groupId = self.getGroupId(group["name"], corpusNewId)
            if groupId is None:
                groupId = self.createBucket(corpusNewId, group["name"])
            groups_dict[oldGroupId] = groupId

            # Ajout des schémas disponibles
            schemas = group["schemas"]
            for schema in schemas:
                schema_file_path = corpus_dir_path.joinpath("groups") \
                    .joinpath(oldGroupId).joinpath(schema["schemaType"]).with_suffix(".schema")
                if schema_file_path.exists():
                    with schema_file_path.open("r", encoding="UTF-8") as schema_file:
                        schema_j = json.load(schema_file)["schema"]["schemaJsonContent"]
                elif schema_file_path.name.lower() == CorpusManager.DOCMETASchema.lower():
                    try:
                        with Path(__file__).parent.joinpath("data").joinpath(CorpusManager.DOCMETA).open(
                                "r", encoding="UTF-8") as docmeta_file:
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
                with p.open("r", encoding="UTF-8") as doc_f:
                    doc_json = json.load(doc_f)
                docOldId = doc_json["id"]
                docId = self.addDocument(corpusNewId, doc_json["text"], doc_json["title"], doc_json["source"],
                                         doc_json["language"])

                # Ajouter les annotations
                for old_group_id, new_group_id in groups_dict.items():
                    annot_file_path = corpus_dir_path.joinpath(groups).joinpath(old_group_id).joinpath(
                        docOldId).with_suffix(".json")
                    if not annot_file_path.exists():
                        continue
                    with annot_file_path.open("r", encoding="UTF-8") as annot_file:
                        annot = json.load(annot_file)
                    if annot is None:
                        continue
                    elif type(annot) == dict:
                        annot = annot[corpusOldId][groupId]

                    for a in annot:
                        del (a["annotationId"])
                        a["_corpus_id"] = corpusNewId
                        a["_documentID"] = docId

                        if "domainName" in a:
                            a["domainName"] = a["domainName"].replace(" ", "")

                        if "domainScore" in a:
                            if a["domainScore"] >= 0.0001:
                                self.addAnnotation(corpusNewId, new_group_id, a)
                        else:
                            self.addAnnotation(corpusNewId, new_group_id, a)
        except IOError as e:
            print("Corpus upload failed : " + str(e))
            return None

        return corpusNewId

    def exportToDisk(self, corpus_id, outputDir, exportGroupIdList=None):

        buckets = defaultdict(list)
        outputPath = Path(outputDir)

        if not outputPath.exists():
            return False

        # Prepare the subfolders
        docFolderPath = outputPath.joinpath("documents")
        groupFolderPath = outputPath.joinpath("groups")

        docFolderPath.mkdir()
        groupFolderPath.mkdir()

        # Download corpus specs and save them
        with outputPath.joinpath("corpus.json").open("w", encoding="UTF-8") as corpus_file:
            json.dump(self.getCorpusMetadata(corpus_id).json(), corpus_file, indent=4)

        # Download the corpus structure and replicate it
        resp = self.config.getRequest(self.config.baseURLPacteBE + "RACSProxy/corpora/" + corpus_id + "/structure",
                                      UserType.CustomUser)

        if resp:
            j = resp.json()
            with outputPath.joinpath(CorpusManager.CORPUS_STRUCT_FILE).open("w", encoding="UTF-8") as struct_file:
                json.dump(j, struct_file, indent=4)

            for b in j.get("buckets", None):
                bucket_id = b["id"]
                if exportGroupIdList is None or bucket_id in exportGroupIdList:
                    groupPath = groupFolderPath.joinpath(bucket_id)
                    groupPath.mkdir()
                    for schema in b["schemas"]:
                        schemaName = schema["schemaType"]
                        buckets[bucket_id].append(schemaName)
                        schemaId = self.getSchemaId(schemaName, corpus_id, bucket_id)
                        if schemaId:
                            with open(groupPath.joinpath(schemaName).with_suffix(".schema"), "w",
                                      encoding="UTF-8") as schema_file:
                                json.dump(self.getSchema(schemaId), schema_file, indent=4)

            # Check if all required groups are in the structure, if not, exit.
            if exportGroupIdList:
                for groupId in exportGroupIdList:
                    if groupId not in buckets:
                        print("Missing group: " + groupId)
                        return False

            # List documents and download them
            docList = self.getDocuments(corpus_id)
            for doc in docList:
                resp = self.config.getRequest(self.config.baseURLPacteBE + "RACSProxy/corpora/" + corpus_id +
                                              "/documents/" + doc.id, UserType.CustomUser)
                with docFolderPath.joinpath(doc.id).with_suffix(".json").open("w", encoding="UTF-8") as doc_file:
                    json.dump(resp.json(), doc_file)

                for groupId, schemas in buckets.items():
                    if len(schemas) > 0:
                        grpschema = dict()
                        grpschema[groupId] = schemas
                        annotationList = self.getAnnotations(corpus_id, doc.id, grpschema)
                        with open(os.path.join(groupFolderPath, groupId, doc.id + ".json"), "w",
                                  encoding="UTF-8") as group_file:
                            json.dump(annotationList, group_file)

            return True

        return False


if __name__ == "__main__":
    print(Path(__file__).parent.joinpath("data").joinpath(CorpusManager.DOCMETASchema))
