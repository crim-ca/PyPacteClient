import json
from enum import Enum

# --- Project Libraries --------------------------------------------------------
from PacteUtil.QuickConfig import QuickConfig
from .BaseService import BaseService


class NerLinkingMethod(Enum):
    Cluster = "cluster"
    AltNameLength = "altnamelength"
    Population = "population"
    Graph = "graph"


class Tools(Enum):
    NER = "ner"
    TIM = "timex"


class SEMservice(BaseService):

    def __init__(self, quicfg: QuickConfig):
        super().__init__(quicfg)
        self.ServiceUrl = self.config.getServiceUrl()
        self.servicename = "pacte_semantic"
        self.tool = Tools.NER.value

        self.docUrl = None
        self.model = None
        self.doLinking = None
        self.linkingMethod = None
        self.reportUrl = None
        self.schemaUpload = None
        self.annotationUploadUrl = None
        self.labels = None
        self.params = None

    def set_options(self, corpus_id: str, doc_url: str, model_name: str, do_linking: bool,
                    linking_method: NerLinkingMethod, reportUrl: str, annotationUploadUrl: str, schemaUploadUrl: str,
                    labels: list, customParams: dict):
        """

        :param corpus_id:
        :param doc_url:
        :param model_name:
        :param do_linking:
        :param linking_method:
        :param reportUrl:
        :param annotationUploadUrl:
        :param schemaUploadUrl:
        :param labels:
        :param customParams:
        :return:
        """
        self.corpusId = corpus_id
        self.docUrl = doc_url
        self.model = model_name
        self.doLinking = do_linking
        self.linkingMethod = linking_method
        self.reportUrl = reportUrl
        self.schemaUpload = schemaUploadUrl
        self.annotationUploadUrl = annotationUploadUrl
        self.labels = labels
        if customParams:
            self.params = customParams

        return True

    def get_json_config(self):
        """
        Get the json config file ready for the service
        :return:
        """

        json_data = json.dumps({})

        json_data["annot_out_url"] = self.annotationUploadUrl
        json_data["corpus_id"] = self.corpusId
        json_data["labels"] = self.labels
        json_data["linking"] = self.doLinking
        json_data["linking_method"] = self.linkingMethod
        json_data["model_name"] = self.model
        json_data["report_out_url"] = self.reportUrl
        json_data["schema_upload_url"] = self.schemaUpload
        json_data["tool"] = self.TOOLNAME
        json_data["params"] = self.params

        return json_data

    def execute(self):
        """
        Run the service
        :return:
        """
        lsResults = self.config.postRequest(
            self.config.getServiceUrl() + "pacte_semantic/process?doc_url=" + self.docUrl,
            self.getJSONConfig, None)
        jres = json.loads(lsResults)
        if "uuid" in jres:
            self.lastUUID = jres["uuid"]

        return self.lastUUID
