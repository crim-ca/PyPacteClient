import json
from json import JSONDecodeError


class Annotation:
    def __init__(self, id, corpusid, type, docid, schematype, offsets):
        self.id = id
        self.corpusid = corpusid
        self.type = type
        self.docid = docid
        self.schematype = schematype
        self.offsets = offsets

    @classmethod
    def from_json(cls, text):
        try:
            input = json.loads(text)
            id = input["annotationId"]
            corpusid = input["_corpusID"]
            type = input["Type"]
            docid = input["_documentID"]
            schematype = input["schemaType"]
            offsets = list()
            for off in input["offsets"]:
                offsets.append({"begin": off["begin"], "end": off["end"]})

            return cls(id, corpusid, type, docid, schematype, offsets)
        except JSONDecodeError as err:
            print("Error reading document file: " + err)
            return
