from enum import Enum

# --- Project Libraries --------------------------------------------------------
from PacteUtil.QuickConfig import QuickConfig
from .BaseService import BaseService


class TsdAnnotationMethod(Enum):
    Most_Probable = "MOST_PROBABLE"
    All_Desambiguated = "ALL_DESAMBIGUATED"


class LexiconFeatures(Enum):
    Description = "description"
    Gender = "gender"
    Number = "number"
    Pos = "pos"


class Tools(Enum):
    TermSense = "tsd"
    TermDomain = "tdi"
    PatternTag = "vettager"


class LEXservice(BaseService):

    def __init__(self, config: QuickConfig):
        super().__init__(config)
        self.serviceUrl = self.config.baseURLService
        self.serviceName = "pacte_lexical"
        self.tool = ""
        self.racsUrl = self.config.baseRacsUrl
        self.docUrl = None
        self.reportUrl = ""
        self.schemaUpload = ""
        self.annotationUploadUrl = ""

        # TDI & TSD
        self.docMetaInfoUrl = ""
        self.corpusMetaInfoUrl = ""
        self.posAnnotationUrl = ""
        self.minConfidence = 0
        self.languageUsed = ""
        self.domainsList = []
        self.snapshotUrl = ""
        self.model_post_url = ""
        self.model_url = ""

        # TDI
        self.topN = 5
        self.createAnnotationFormat = ""

        # TSD
        self.annotation_method = TsdAnnotationMethod.Most_Probable.value
        self.custom_schema_name = ""
        self.lexicon_features = []

        # VET

    def set_options_tsd(self, corpus_id: str, doc_url: str, annotation_upload_url: str, report_url: str,
                        schema_upload_url: str, doc_meta_info_url: str, corpus_meta_info_url: str,
                        pos_annotation_url: str, annotation_method: TsdAnnotationMethod, min_confidence: int,
                        custom_schema_name: str, language: str, domains: list, model_url: str, snapshot_url: str,
                        model_post_url: str, lexicon_features: list):
        """

        :param corpus_id:
        :param doc_url:
        :param annotation_upload_url:
        :param report_url:
        :param schema_upload_url:
        :param doc_meta_info_url:
        :param corpus_meta_info_url:
        :param pos_annotation_url:
        :param annotation_method:
        :param min_confidence:
        :param custom_schema_name:
        :param language:
        :param domains:
        :param model_url:
        :param snapshot_url:
        :param model_post_url:
        :param lexicon_features:
        :return:
        """

        self.tool = Tools.TermSense.value
        self.corpusId = corpus_id
        self.docUrl = doc_url
        self.docMetaInfoUrl = doc_meta_info_url
        self.corpusMetaInfoUrl = corpus_meta_info_url
        self.reportUrl = report_url
        self.schemaUpload = schema_upload_url
        self.annotationUploadUrl = annotation_upload_url
        self.posAnnotationUrl = pos_annotation_url
        self.languageUsed = language
        self.domainsList = domains
        self.model_url = model_url
        self.snapshotUrl = snapshot_url
        self.model_post_url = model_post_url
        self.minConfidence = min_confidence

        self.annotation_method = annotation_method
        self.custom_schema_name = custom_schema_name
        self.lexicon_features = lexicon_features

        pass

    def set_options_vetagger(self):
        self.tool = Tools.PatternTag.value
        pass

    def set_options_tdi(self, corpus_id: str, doc_url: str, doc_meta_info_url: str, corpus_meta_info_url: str,
                        report_url: str, annotation_upload_url: str, schema_upload_url: str,
                        pos_annotation_url: str, top_n: int, min_confidence: int, create_annotation_format: str,
                        language: str, domains: list, snapshot_url: str, model_post_url: str, model_url: str):
        """

        :param corpus_id:
        :param doc_url:
        :param doc_meta_info_url:
        :param corpus_meta_info_url:
        :param report_url:
        :param annotation_upload_url:
        :param schema_upload_url:
        :param pos_annotation_url:
        :param top_n:
        :param min_confidence:
        :param create_annotation_format:
        :param language:
        :param domains:
        :param snapshot_url:
        :param model_post_url: Url to save the model
        :param model_url: Url to load the model from
        :return:
        """
        self.corpusId = corpus_id
        self.docUrl = doc_url
        self.docMetaInfoUrl = doc_meta_info_url
        self.corpusMetaInfoUrl = corpus_meta_info_url
        self.reportUrl = report_url
        self.schemaUpload = schema_upload_url
        self.annotationUploadUrl = annotation_upload_url
        self.tool = Tools.TermDomain.value

        self.posAnnotationUrl = pos_annotation_url
        self.topN = top_n
        self.minConfidence = min_confidence
        self.createAnnotationFormat = create_annotation_format
        self.languageUsed = language
        self.domainsList = domains
        self.snapshotUrl = snapshot_url
        self.model_post_url = model_post_url
        self.model_url = model_url

        return True

    def get_json_config(self):
        """
        Get the json config file ready for the last parametered tool
        :return:
        """
        json_data = dict()
        json_data["corpus_id"] = self.corpusId
        json_data["tool"] = self.tool
        if self.tool in [Tools.TermDomain.value, Tools.TermSense.value]:
            json_data["annot_out_url"] = self.annotationUploadUrl
            json_data["report_out_url"] = self.reportUrl
            json_data["schema_upload_url"] = self.schemaUpload
            json_data["doc_meta_info_url"] = self.docMetaInfoUrl
            json_data["corpus_meta_info_url"] = self.corpusMetaInfoUrl
            json_data["pos_annotation_url"] = self.posAnnotationUrl
            json_data["minConfidence"] = self.minConfidence
            json_data["language"] = self.languageUsed
            json_data["domains"] = str(self.domainsList)

            if not self.snapshotUrl == "":
                json_data["snapshot_url"] = self.snapshotUrl
            else:
                json_data["model_url"] = self.model_url
            json_data["model_post_url"] = self.model_post_url

            if self.tool == Tools.TermDomain.value:
                json_data["topN"] = self.topN
                json_data["createAnnotationFormat"] = self.createAnnotationFormat

            if self.tool == Tools.TermSense.value:
                json_data["lexiconFeatures"] = "[\"description\", \"gender\"]"  # self.lexicon_features
                json_data["annotate"] = self.annotation_method
                json_data["customSchemaName"] = self.custom_schema_name

        return json_data
