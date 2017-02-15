import os

from Bio import SeqIO


def get_feature_seq(parent_seq, bio_feature):
    return bio_feature.extract(parent_seq)


def get_object_id_from_file_name(file_name):
    return file_name[0:-3].replace(' ', '')


def get_object_id_from_file_path(file_path):
    file_name = os.path.basename(file_path)
    return get_object_id_from_file_name(file_name)


def get_biopython_object(path):
    if not os.path.isfile(path):
        msg = "%s is not a valid file" % path
        raise IOError(msg)

    biopython_object_list = list(SeqIO.parse(path, 'genbank'))
    if len(biopython_object_list) > 0:
        return biopython_object_list[0]
