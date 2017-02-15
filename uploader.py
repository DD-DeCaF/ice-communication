import json
import os

from comm import IceCommunication
from iceelements import Feature, PlasmidContainer, get_id_from_ice_data
from utils import get_feature_seq

from settings import IceSettings


class IceUploader(object):
    def __init__(self):
        super(IceUploader, self).__init__()

        setting = IceSettings()
        self.comm = IceCommunication(setting)

    def upload_part(self, part):
        return json.loads(self.comm.ice_post_request("rest/parts", str(part)))

    def upload_seq_file(self, genbank_file_path, ice_id, entry_type='plasmid'):
        file_name = os.path.basename(genbank_file_path)
        with open(genbank_file_path, 'r') as fd:
            files = {
                'file': (file_name, fd.read(), 'text/plain'),
                'entryRecordId': str(ice_id),
                'entryType': str(entry_type)
            }
            self.comm.ice_post_file_request("rest/file/sequence", files)

    def upload_seq(self, ice_id, seq):
        data = {
            'sequence': str(seq)
        }
        self.comm.ice_post_request('rest/parts/%s/sequence' % str(ice_id), data)

    def link_to_child(self, parent_ice_id, child_data):
        self.comm.ice_post_request('rest/parts/%s/links' % parent_ice_id, child_data)

    def upload_part_with_file_seq(self, container):
        # Upload plasmid
        plasmid_ice_data = self.upload_part(container.part)
        plasmid_ice_id = get_id_from_ice_data(plasmid_ice_data)
        self.upload_seq_file(container.file_path, plasmid_ice_id)
        return plasmid_ice_data

    def upload_feature_with_seq(self, feature, feature_seq):
        ice_feature_data = self.upload_part(feature)
        if 'id' not in ice_feature_data:
            msg = 'Could not find "id" in the returned data'
            raise AttributeError(msg)

        self.upload_seq(ice_feature_data['id'], feature_seq)
        return ice_feature_data

    def upload_plasmid_genbank_file(self, file_path):
        container = PlasmidContainer(file_path)
        plasmid_ice_data = self.upload_part_with_file_seq(container)

        parent_ice_id = get_id_from_ice_data(plasmid_ice_data)

        for i, bio_feature in enumerate(container.bio_object.features):
            feature_ice_data = self.upload_feature_with_seq(Feature(bio_feature),
                                                            get_feature_seq(container.bio_object.seq, bio_feature))

            self.link_to_child(parent_ice_id, feature_ice_data)