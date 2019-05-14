# --- System Libraries ---------------------------------------------------------
import json
import os


class Annotation:
    """
    Pacte annotation structure
    """
    def __init__(self, j):
        self.offsets = []
        self.features = {}
        self.type = ""
        self.id = ""
        self.cible = ""

        if j.get("offsets", None):
            for elem in j["offsets"]:
                self.offsets.append((elem["begin"], elem["end"]))
            self.cible = "surface"
        elif j.get("_documentID", None):
            self.cible = "document"
        else:
            self.cible = "corpus"
        self.type = j["schemaType"]
        self.id = j["annotationId"]
        # ajouter les features
        for k, v in j.items():
            if k not in ["_corpusID", "_documentID", "offsets", "schemaType",
                         "annotationId"]:
                self.features[k] = v

    def iscontiguous(self, other) -> bool:
        """
        Check if the two annotations of the same type are contiguous on at
        least one offset, or are separated only
        by non printable characters
        :param other: the other annotation to check
        :return: True if annotations are contiguous
        """
        for pos in self.offsets:
            for opos in other.offsets:
                if list(set(range(int(pos[0]), int(pos[1])))
                        & set(range(int(opos[0]), int(opos[1])))):
                    # print(str(pos) + " : " + str(opos) + " >> contiguous")
                    return True


class Document:
    """
    Pacte document structure
    """
    def __init__(self):
        self.text = ""
        self.id = ""
        self.file = ""
        self.language = ""
        self.annotations = []

    def merge_annotations(self):
        """
        Joindre les annotations contigues
        :return: None
        """
        for a in self.annotations:
            for b in self.annotations:
                if not a == b and a.type == b.type and a.features == b.features:
                    if a.iscontiguous(b):
                        # print("Should merge " + str(a) + " and " + str(b))
                        a.offsets[0] = \
                            (a.offsets[0][0]
                             if a.offsets[0][0] < b.offsets[0][0]
                             else b.offsets[0][0],
                             b.offsets[0][1]
                             if b.offsets[0][1] > a.offsets[0][1]
                             else a.offsets[0][1])
                        self.annotations.remove(b)
                    else:
                        # TODO: support multi-offset annotation
                        # Check if separated only by white space and skips
                        if a.offsets[0][1] < b.offsets[0][0]:
                            start = a.offsets[0][1]
                            end = b.offsets[0][0]
                        else:
                            start = b.offsets[0][1]
                            end = a.offsets[0][0]

                        if len(self.text[start:end].strip()) == 0:
                            a.offsets[0] = \
                                (a.offsets[0][0]
                                 if a.offsets[0][0] < b.offsets[0][0]
                                 else b.offsets[0][0],
                                 b.offsets[0][1]
                                 if b.offsets[0][1] > a.offsets[0][1]
                                 else a.offsets[0][1])
                            self.annotations.remove(b)


class PacteCorpusReader:

    def __init__(self, corpus_path, schemas, skipline_replacement):
        """
        Iterate over the document and annotations of a Pacte corpus
        :param self:
        :param corpus_path: Path of the exportToDisk function from PacteClient
        :param schemas: List of schemas to read
        :return:
        """
        if not os.path.isdir(os.path.join(corpus_path, "documents")) or \
                not os.path.exists(os.path.join(corpus_path, "documents")):
            raise Exception('Invalid directory: ' + corpus_path)
        self.root = corpus_path
        self.list = os.scandir(os.path.join(corpus_path, "documents"))
        self.schemas = schemas
        if not skipline_replacement:
            self.skipline_replacement = None
        else:
            self.skipline_replacement = skipline_replacement

    def __iter__(self):
        return self

    def __next__(self):
        f = next(self.list)
        if not f:
            raise StopIteration()

        doc = Document()
        doc.file = f.path
        doc.id = f.name[0:36]
        j = json.load(open(f.path))
        if self.skipline_replacement:
            doc.text = j["text"].replace('\r\n', self.skipline_replacement) \
                .replace('\n', self.skipline_replacement)
        else:
            doc.text = j["text"]
        doc.language = j["language"]
        doc.id = j["id"]

        # check for annotations in each group
        for p in os.scandir(os.path.join(self.root, "groups")):
            anfile = os.path.join(self.root, "groups", p.name, doc.id + ".json")
            if os.path.isfile(anfile):
                an = json.load(open(anfile))
                for k1, v1 in an.items():
                    for k2, v2 in v1.items():
                        for k3, v3 in v2.items():
                            if not self.schemas or v3[0]["schemaType"] \
                                    in self.schemas:
                                for a in v3:  # Convert annotation to object
                                    doc.annotations.append(Annotation(a))
        return doc

