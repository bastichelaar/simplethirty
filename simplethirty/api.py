import os
import json
import requests
from requests.auth import HTTPBasicAuth


"""Base class for requests to the 30loops API. It serves as a HTTP mixin
class for all handlers that are talking to an API endpoint."""
def request(uri, method='GET', context=None, message=None, headers=None):
    # additional arguments for the http request
    kwargs = {}

    if message:
        kwargs['data'] = message

    if context['username'] and context['password']:
        kwargs['auth'] = HTTPBasicAuth(
                username=context['username'],
                password=context['password'])
        if headers is None:
            headers = {}
    headers['Accept'] = "application/json"

    ssl_cert = os.path.join(
            os.path.dirname(__file__), "ssl", "StartSSL_CA.pem")
    kwargs['verify'] = ssl_cert

    try:
        response = requests.request(
                method=method.lower(),
                url=uri,
                **kwargs)
    except requests.ConnectionError:
        pass

    bad_statuses = [400, 401, 403, 404]

    if response.status_code in bad_statuses:
        error = json.loads(response.content)
        return error

    error_statuses = [500, 501, 502, 503, 504]

    if response.status_code in error_statuses:
        pass

    return response
