import json
import os
from urllib.error import HTTPError
import shutil
import tempfile
import requests


def check_response(response):
    if response.status_code != 200:
        raise HTTPError(response.url, response.status_code,
                        msg=response.text, hdrs=response.headers, fp="")
    return True


class IceCommunication(object):
    def __init__(self, settings):

        super(IceCommunication, self).__init__()

        self.settings = settings

        self.token = None
        if settings.user_name and settings.password:
            self.token = self.get_token()

    def add_custom_field(self, part_id, field_name, field_value):
        data = {
            'edit': True,
            'name': field_name,
            'nameInvalid': False,
            'partId': part_id,
            'value': field_value,
            'valueInvalid': False
        }

        self.ice_post_request('rest/custom-fields', data)

    def get_request_url(self, rest_url=None):
        if rest_url:
            return "https://{}:{}/{}".format(self.settings.host, self.settings.port, rest_url)
        return "https://{}:{}".format(self.settings.host, self.settings.port)

    def get_request_header_default(self):

        if self.token:
            return {
                "X-ICE-Authentication-SessionId": self.token
            }

        if not self.settings.api_key:
            raise KeyError("The api-key have not been set")
        if not self.settings.api_user:
            raise KeyError("The api user have not been set")

        headers = {
            "X-ICE-API-Token-Client": self.settings.api_user,
            "X-ICE-API-Token": self.settings.api_key
        }
        return headers

    def ice_get_request(self, rest_url, params=None):
        request_url = self.get_request_url(rest_url)
        headers = self.get_request_header_default()

        response = requests.get(request_url,
                                params=params,
                                verify=False,
                                headers=self.get_request_header_default()
                                )
        if check_response(response):
            return response.text

    def get_ice_part(self, ice_id):
        '''This class is for backwards compatibility'''
        return self.get_ice_part_detail(ice_id)

    def get_ice_part_detail(self, ice_id):
        rest_url = "rest/parts/{}".format(ice_id)
        return self.ice_get_request(rest_url)

    def get_ice_part_list(self):
        '''There doesn't seem to be a list view in ICE, 
        so this is a hack to get it done. Pagination is missing though'''
        rest_url = "rest/parts/"
        return self.search_ice_part('')

    def search_ice_part(self, query, offset=0, limit=15, sort='relevance', asc='false'):
        rest_url = "rest/search?"
        search_string = "q={}&offset={}&limit={}&sort={}&asc={}".format(
            query, offset, limit, sort, asc)
        return self.ice_get_request(rest_url + search_string)

    def get_ice_part_sequence(self, ice_id):
        rest_url = "rest/parts/{}/sequence".format(ice_id)
        return self.ice_get_request(rest_url)

    def ice_post_request(self, rest_url, data, json_content=True, headers=None):
        print(headers)
        if not headers:
            headers = self.get_request_header_default()
        if json_content:
            headers["Content-type"] = "application/json"

        response = requests.post(self.get_request_url(rest_url),
                                 data=str(data),
                                 verify=False,
                                 headers=headers
                                 )
        check_response(response)
        return response.text

    def ice_post_file_request(self, rest_url, files):
        headers = self.get_request_header_default()

        response = requests.post(self.get_request_url(rest_url),
                                 files=files,
                                 verify=False,
                                 headers=headers
                                 )
        check_response(response)
        return response.text

    def get_token(self):
        headers = {'Content-type': 'application/json'}
        data = {
            'email': self.settings.user_name,
            'password': self.settings.password
        }

        ice_responds = json.loads(self.ice_post_request(
            'rest/accesstokens', data, headers=headers))
        if 'sessionId' in ice_responds:
            return ice_responds['sessionId']

    def download_genbank(self, ids, file_path='./'):
        url = 'rest/file/csv?sequenceFormats=genbank'
        data = {'all': False,
                'destination': [],
                'selectionType': 'COLLECTION',
                'entries': ids}

        temp = json.loads(self.ice_post_request(url, data))

        if 'value' in temp:
            file_name = temp['value']
        else:
            raise HTTPError(url, 500, 'Could not download file')

        get_url = 'rest/file/tmp/{}'.format(file_name)

        request_url = self.get_request_url(get_url)

        response = requests.get(request_url,
                                verify=False,
                                headers=self.get_request_header_default(),
                                stream=True)

        check_response(response)

        full_file_path = os.path.join(file_path, file_name)

        with open(full_file_path, 'wb') as fd:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, fd)

        return True

    def get_genbank_record(self, part_id):
        '''Because of a bug in ICE, the genbank file can't be turned 
        into a biopython object. Returns a genbank file object from 
        the part_id'''
        url = 'rest/file/csv?sequenceFormats=genbank'
        data = {'all': False,
                'destination': [],
                'selectionType': 'COLLECTION',
                'entries': [part_id]}

        temp = json.loads(self.ice_post_request(url, data))

        if 'value' in temp:
            file_name = temp['value']
        else:
            raise HTTPError(url, 500, 'Could not download file')

        get_url = 'rest/file/tmp/{}'.format(file_name)

        request_url = self.get_request_url(get_url)

        response = requests.get(request_url,
                                verify=False,
                                headers=self.get_request_header_default(),
                                stream=True)

        # Since the file is a binary zip file, some hoops needs to be jumped
        tmp = tempfile.TemporaryFile()
        tmp.write(response.raw.data)
        z = zipfile.ZipFile(tmp)
        # The entry file is not needed, when there is only a single file
        file_name = z.namelist.remove('entries.csv')[0]
        return z.open(file_name)
