"""Optional SPARQL 1.1 protocol client. Server provisioning is explicit."""
from dataclasses import dataclass
import os
from urllib.parse import urlparse
import requests
from rdflib import Graph

@dataclass(frozen=True)
class Endpoint:
    query_url: str
    update_url: str | None = None
    timeout_seconds: float = 20.0
    allowed_host: str = 'localhost'

class SparqlClient:
    def __init__(self, endpoint: Endpoint):
        for url in filter(None,[endpoint.query_url,endpoint.update_url]):
            parsed=urlparse(url)
            if parsed.scheme not in {'http','https'} or parsed.hostname != endpoint.allowed_host:
                raise ValueError('Endpoint must match the configured host and use HTTP(S).')
            if parsed.scheme=='http' and parsed.hostname not in {'localhost','127.0.0.1','::1'}:
                raise ValueError('Use HTTPS for non-local endpoints.')
        self.endpoint=endpoint
        self.session=requests.Session()
        user=os.getenv('SPARQL_USER'); password=os.getenv('SPARQL_PASSWORD')
        if user and password:self.session.auth=(user,password)

    def _post(self,url,text,content_type,accept):
        response=self.session.post(url,data=text.encode('utf-8'),
            headers={'Content-Type':content_type,'Accept':accept},
            timeout=self.endpoint.timeout_seconds,allow_redirects=False)
        response.raise_for_status()
        if 300 <= response.status_code < 400:raise RuntimeError('Redirect requires explicit endpoint review.')
        return response

    def select_or_ask(self,text):
        return self._post(self.endpoint.query_url,text,'application/sparql-query',
                          'application/sparql-results+json').json()

    def construct_or_describe(self,text):
        response=self._post(self.endpoint.query_url,text,'application/sparql-query','text/turtle')
        return Graph().parse(data=response.text,format='turtle')

    def update(self,text,*,enabled=False):
        if not enabled or not self.endpoint.update_url:
            raise ValueError('Configure an update endpoint and explicitly enable updates.')
        self._post(self.endpoint.update_url,text,'application/sparql-update','*/*')

    def close(self):
        self.session.close()
