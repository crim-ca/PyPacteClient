import json


class Group:
    def __init__(self, id: str, name: str, schemas: list):
        self.name = name
        self.id = id
        self.schemas = schemas


class CorpusStructure:

    def __init__(self, groups: list):
        self.groups = groups

    @classmethod
    def from_file(cls, filepath):
        try:
            groups = list()
            input = json.loads(open(filepath).read())

            for bucket in input["buckets"]:
                id = bucket["id"]
                name = bucket["name"]
                schemaslist = list()
                for schema in bucket["schemas"]:
                    schemaslist.append(schema["schemaType"])
                groups.append(Group(id, name, schemaslist))

            return cls(groups)
        except:
            print("Error reading document file")
            return

    def find_group(self, schema_name: str):
        '''
        Find the corresponding group for an annotation type
        :param schema_name:
        :return:
        '''
        groups = list()
        for g in self.groups:
            if schema_name in g.schemas:
                groups.append(g.id)

        return groups
