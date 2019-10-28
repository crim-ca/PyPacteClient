from enum import Enum
import json
import os
from PacteClient.FeatureDefinition import FeatureDefinition


class TARGET(Enum):
    document_surface1d = 1
    document = 2
    corpus = 3


class SchemaData(object):
    featureList = []  # Les attributs du schéma
    schemaType = ""
    targetType = ""

    def __init__(self, schema_target: TARGET, schema_type: str, features: dict):
        self.targetType = schema_target
        self.schemaType = schema_type
        self.featureList = features

    @classmethod
    def schema_from_json(cls, json_definition: str):
        jschema = json.loads(json_definition)

        # If the schema comes from racs backend
        if "schema" in jschema:
            jschema = json.loads(jschema["schema"]["schemaJsonContent"])

        prop_schema = jschema["properties"]
        feats = dict()
        for key in prop_schema:
            if not ("," + key.lower() + ",") in ",schematype,corpusid,documentid,offsets,":
                feats[key] = FeatureDefinition.init_from_json(key, json.dumps(prop_schema[key]))

        return cls(jschema["targetType"], jschema["schemaType"], feats)

    def to_string(self):
        url = ""
        required = ""
        features = ""
        baseschema = ""

        if self.targetType.name == TARGET.document_surface1d.name:
            url = "data/surface1d_schema.json"
        elif self.targetType.name == TARGET.document.name:
            url = "data/document_schema.json"
        elif self.targetType.name == TARGET.corpus.name:
            url = "data/corpus_schema.json"

        with open(os.path.join(os.path.dirname(__file__), url), 'r', encoding="UTF-8") as fs:
            schematext = fs.readlines()
        baseschema = "".join(schematext)

        # Change name
        schema = baseschema.replace("###TEMPLATETYPE###", self.schemaType)
        schema = schema.replace("###TEMPLATETITLE###", self.schemaType)

        # Generate features
        if self.featureList:
            for opt in self.featureList:
                features += ', "' + opt + '":' + self.featureList[opt].string_definition()
                if self.featureList[opt].isRequired:
                    required += ',"' + self.featureList[opt].name + '"'

        # Insert features at the end of the schema
        if not self.featureList or len(self.featureList) == 0:
            schema = schema.replace("###CUSTOMFEATURESLIST###", "")
            schema = schema.replace("###CUSTOMREQUIREDFIELDS###", "")

        elif len(features) > 0:
            schema = schema.replace("###CUSTOMFEATURESLIST###", features)
            if required:
                schema = schema.replace("###CUSTOMREQUIREDFIELDS###", required)
            else:
                schema = schema.replace("###CUSTOMREQUIREDFIELDS###", "")

        return schema
