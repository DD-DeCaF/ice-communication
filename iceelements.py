import json

from utils import get_biopython_object
from utils import get_object_id_from_file_path


class Part(object):
    def __init__(self):  # , record_id):
        self.type = "PART"
        self.name = ""
        # self.recordId = record_id
        self.keywords = ""
        self.shortDescription = ""
        self.longDescription = ""
        self.references = ""
        self.bioSafetyLevel = 1
        self.intellectualProperty = ""
        self.links = []
        self.principalInvestigator = ""
        self.principalInvestigatorEmail = ""
        self.selectionMarkers = []
        self.fundingSource = ""
        self.parameters = []
        self.strainData = {}
        self.plasmidData = {}
        self.arabidopsisSeedData = {}

    def __str__(self):
        return json.dumps(self.__dict__)


class Plasmid(Part):
    def __init__(self, biopython_obj, name=None):
        super(Plasmid, self).__init__()

        self.type = "PLASMID"

        self.name = biopython_obj.name
        if name:
            self.name = name

        if 'keywords' in biopython_obj.annotations:
            self.keywords = ",".join(biopython_obj.annotations['keywords'])
        self.shortDescription = biopython_obj.description
        self.plasmidData = {
            "backbone": "",
            "originOfReplication": "",
            "promoters": "",
            "circular": True,
            "replicatesIn": ""
        }


class Feature(Part):
    def __init__(self, biopython_feature):
        super(Feature, self).__init__()

        feature_name = biopython_feature.id
        if biopython_feature.type == 'gene':
            qualifiers = biopython_feature.qualifiers
            if 'gene' in qualifiers:
                feature_name = '_'.join(qualifiers['gene'])

        self.name = feature_name


class Strain(Part):
    def __init__(self, biopython_obj):
        super(Strain, self).__init__()
        self.name = biopython_obj.name
        self.host = ""
        self.genotypePhenotype = ""


class PartContainer(object):
    def __init__(self, file_path):
        super(PartContainer, self).__init__()

        self.file_path = file_path
        self.bio_object = get_biopython_object(file_path)
        self.part = None


class PlasmidContainer(PartContainer):
    def __init__(self, file_path):
        super(PlasmidContainer, self).__init__(file_path)

        plasmid_name = None
        if self.bio_object.name == 'Exported':
            plasmid_name = get_object_id_from_file_path(file_path)

        self.part = Plasmid(self.bio_object, plasmid_name)


class StrainContainer(PartContainer):
    def __init__(self, file_path):
        super(StrainContainer, self).__init__(file_path)
        self.part = Strain(self.bio_object)


def get_id_from_ice_data(ice_data):
    if 'id' not in ice_data:
        msg = 'Could not find "id" in the returned data'
        raise AttributeError(msg)
    return ice_data['id']
