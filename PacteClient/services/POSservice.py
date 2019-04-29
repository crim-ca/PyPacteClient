import json
from enum import Enum

# --- Project Libraries --------------------------------------------------------
from PacteUtil.QuickConfig import QuickConfig
from .BaseService import BaseService


class Tools(Enum):
    Tokenizer = "tokenizer"
    POStagger = "postagger"
    Stemmer = "stemmer"
    Chunker = "chunker"


class POSservice(BaseService):

    def __init__(self, config: QuickConfig):
        super().__init__(config)
        self.serviceUrl = self.config.baseURLService
        self.serviceName = "pacte_linguistic"
        self.tool = Tools.Tokenizer
        self.racsUrl = self.config.baseRacsUrl

        self.docUrl = None
        self.model = None
        self.reportUrl = ""
        self.schemaUpload = ""
        self.annotationUploadUrl = ""
        self.docMetaInfoUrl = ""
        self.corpusMetaInfoUrl = ""

    def set_options(self, corpusId: str, docUrl: str, docMetaInfoUrl: str, corpusMetaInfoUrl: str,
                    reportUrl: str, annotationUploadUrl: str, schemaUploadUrl: str, tool:Tools):
        """

        :param corpusId:
        :param docUrl:
        :param docMetaInfoUrl:
        :param corpusMetaInfoUrl:
        :param reportUrl:
        :param annotationUploadUrl:
        :param schemaUploadUrl:
        :return:
        """
        self.corpusId = corpusId
        self.docUrl = docUrl
        self.docMetaInfoUrl = docMetaInfoUrl
        self.corpusMetaInfoUrl = corpusMetaInfoUrl
        self.reportUrl = reportUrl
        self.schemaUpload = schemaUploadUrl
        self.annotationUploadUrl = annotationUploadUrl
        self.tool = tool

        return True

    def get_json_config(self):
        """
        Get the json config file ready for the service
        :return:
        """

        json_data = {}

        json_data["corpus_id"] = self.corpusId
        json_data["annot_out_url"] = self.annotationUploadUrl
        json_data["report_out_url"] = self.reportUrl
        json_data["schema_upload_url"] = self.schemaUpload
        json_data["doc_meta_info_url"] = self.docMetaInfoUrl
        json_data["corpus_meta_info_url"] = self.corpusMetaInfoUrl
        json_data["tool"] = self.tool

        return json_data
