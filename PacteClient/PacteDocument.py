import json


class PacteDocument:

    def __init__(self, id, title, content, source, language, doc_size=None, date_added=None, path=None):
        self.id = id
        self.title = title
        self.content = content
        self.source = source
        self.language = language
        self.docSize = doc_size
        self.dateAdded = date_added
        self.path = path

    @classmethod
    def from_file(cls, filepath):
        try:
            input = json.loads(open(filepath).read())
            id = input["id"]
            title = input["title"]
            content = input["text"]
            source = input["source"]
            language = input["language"]
            doc_size = len(content)

            return cls(id, title, content, source, language, doc_size, None, None)
        except:
            print("Error reading document file")
            return
