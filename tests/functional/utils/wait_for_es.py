import time

from elasticsearch import Elasticsearch
from tests.functional.settings import test_settings

if __name__ == '__main__':
    es_client = Elasticsearch(hosts=test_settings.es_host_url, validate_cert=False, use_ssl=False)

    time.sleep(1)

    while True:
        if es_client.ping():
            break
        time.sleep(1)
    es_client.close()
