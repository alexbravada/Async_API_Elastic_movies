import logging

from elasticsearch import Elasticsearch, TransportError
from tests.functional.settings import test_settings
from tests.functional.utils.backoff import backoff

logging.basicConfig(
    filename='es_ping.log',
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    level=logging.INFO
)

@backoff(log=logging, exception=TransportError)
def wait_for_es(es_client):
    while True:
        if es_client.ping():
            break


if __name__ == '__main__':
    es_client = Elasticsearch(hosts=test_settings.es_host_url, validate_cert=False, use_ssl=False)

    wait_for_es(es_client)

    es_client.close()
