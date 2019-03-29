

class PacteDocument:

    def __init__(self, id, title, content, source, language,
			docSize=None, dateAdded=None, path=None):
            self.id = id
            self.title = title
            self.content = content
            self.source = source
            self.language = language
            self.docSize = docSize
            self.dateAdded = dateAdded
            self.path = path