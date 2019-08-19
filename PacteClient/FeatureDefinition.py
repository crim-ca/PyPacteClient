import json


class FeatureDefinition(object):
    searchable = False
    description = ""
    searchModes = []
    type = ""
    name = ""
    default = ""
    isRequired = False

    def __init__(self, name: str, schema_type: str, description: str, default: str, searchable: bool,
                 search_modes: list):
        self.name = name
        self.type = schema_type
        self.default = default
        self.description = description
        self.searchable = searchable
        self.searchModes = search_modes

    @classmethod
    def init_from_json(cls, json_def: str):
        data = json.loads(json_def)
        return cls(data["name"], data["type"], data["description"], data["default"], data["searchable"],
                   data["searchModes"])

    def string_definition(self):
        return self.json_definition()

    def json_definition(self):
        struct = dict()
        struct["name"] = self.name
        struct["type"] = self.type
        struct["description"] = self.description
        struct["default"] = self.default
        struct["searchable"] = self.searchable
        struct["searchModes"] = self.searchModes
        # struct["required"] = self.isRequired

        return json.dumps(struct)
