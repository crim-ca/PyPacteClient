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
                 search_modes: list, required: bool):
        self.name = name
        self.type = schema_type
        self.default = default
        self.description = description
        self.searchable = searchable
        self.searchModes = search_modes
        self.isRequired = required

    @classmethod
    def init_from_json(cls, schema_name: str, json_def: str):
        data = json.loads(json_def)
        sch_type = ""
        sch_default = None
        requ = None

        if "type" in data:
            sch_type = data["type"]
        elif "targettype" in data:
            sch_type = data["targettype"]

        if "default" in sch_type:
            sch_default = data["default"]

        if "required" in data:
            requ = data["required"]

        return cls(schema_name, sch_type, data["description"], sch_default, data["searchable"], data["searchModes"],
                   requ)

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
        struct["required"] = self.isRequired

        return json.dumps(struct)
