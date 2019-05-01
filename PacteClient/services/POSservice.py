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

    def set_options(self, corpus_id: str, doc_url: str, doc_meta_info_url: str, corpus_meta_info_url: str,
                    report_url: str, annotation_upload_url: str, schema_upload_url: str, tool: Tools):
        """
        Set execution paramters for the service
        :param corpus_id:
        :param doc_url:
        :param doc_meta_info_url:
        :param corpus_meta_info_url:
        :param report_url:
        :param annotation_upload_url:
        :param schema_upload_url:
        :param tool:
        :return:
        """
        self.corpusId = corpus_id
        self.docUrl = doc_url
        self.docMetaInfoUrl = doc_meta_info_url
        self.corpusMetaInfoUrl = corpus_meta_info_url
        self.reportUrl = report_url
        self.schemaUpload = schema_upload_url
        self.annotationUploadUrl = annotation_upload_url
        self.tool = tool

        return True

    def get_json_config(self):
        """
        Get the json config file ready for the service
        :return:
        """
        json_data = dict()
        json_data["corpus_id"] = self.corpusId
        json_data["tool"] = self.tool
        if self.tool == "postagger":
            json_data["annot_out_url"] = self.annotationUploadUrl
            json_data["report_out_url"] = self.reportUrl
            json_data["schema_upload_url"] = self.schemaUpload
            json_data["doc_meta_info_url"] = self.docMetaInfoUrl
            json_data["corpus_meta_info_url"] = self.corpusMetaInfoUrl

        return json_data
