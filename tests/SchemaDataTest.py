# --- System Libraries ---------------------------------------------------------
import unittest

# --- Project Libraries --------------------------------------------------------
from PacteUtil.QuickConfig import QuickConfig
from PacteClient.SchemaData import SchemaData, TARGET
from PacteClient.FeatureDefinition import FeatureDefinition

QuickConfig.config_file_path = "config.properties"


class TestSchemaData(unittest.TestCase):

    def test_loading(self):
        text_definition: str = None
        schema: SchemaData = None

        fschema = open("testdata/document.json", 'r', encoding='UTF-8')
        text_definition = "".join(fschema.readlines())
        fschema.close()

        schema = SchemaData.schema_from_json(text_definition)
        self.assertIsNotNone(schema)
        self.assertEqual("document", schema.targetType)
        self.assertEqual("document", schema.schemaType)

        # Test the search modes
        schema.featureList["commentaire"] = FeatureDefinition("commentaire", "string", "Notes sur l'annotation",
                                                              "default", True, ["noop"], True)
        schema.targetType = TARGET.document
        same_schema = SchemaData.schema_from_json(schema.to_string())

        self.assertTrue("commentaire" in schema.featureList)
        self.assertTrue("commentaire" in same_schema.featureList)

    def test_instantiate(self):
        feats = list()
        feats.append(
            FeatureDefinition("commentaire", "string", "Notes sur l'annotation", "default", True, ["basic"], True))
        scheme = SchemaData(TARGET.document_surface1d, "test", feats)
        self.assertTrue("commentaire" in (x.name for x in scheme.featureList))
        self.assertEqual(1, len(scheme.featureList))
