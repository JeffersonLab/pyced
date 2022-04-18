"""This module contains any network specific code.  Currently defines single class for accessing system trust store."""

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.ssl_ import create_urllib3_context


class SSLContextAdapter(HTTPAdapter):
    """An HTTPAdapter that loads the default system SSL trust store

    This is needed since the requests module ships with its own CA cert store that does not include the JLab PKI"""

    def init_poolmanager(self, *args, **kwargs):
        """Overrides the parent method to include call to load_default_certs()"""
        context = create_urllib3_context()
        kwargs['ssl_context'] = context
        context.load_default_certs()  # this loads the OS default trusted CA certs
        return super(SSLContextAdapter, self).init_poolmanager(*args, **kwargs)


def requests_get(url: str, params: dict, verify: bool, **kwargs) -> requests.Response:
    """A standard get request that optionally uses a custom SSLContextAdapter to pickup Linux system trust store.

    Args:
        url:  The URL to send a get request
        params:  A dictionary of parameters to include in the request
        verify:  Should SSL verification be attempted.

    Returns:
        The response object generated by the GET request.

    Raises:
        ValueError: If the remote server responds with an HTTP response code != 200.
    """
    if verify:
        # Construct a custom SSLContextAdapter to pickup system Trust store on RHEL.
        with requests.Session() as s:
            adapter = SSLContextAdapter()
            s.mount(url, adapter)
            response = s.get(url, params=params, verify=True, **kwargs)
    else:
        response = requests.get(url, params=params, verify=False, **kwargs)

    # It seem like the CED only sends 200.
    if response.status_code != 200:
        raise ValueError(f"Received status_code={response.status_code} (non-OK) response from {response.request.url}. "
                         f"response='{' '.join(response.text[0:20].strip().splitlines())} ...'")

    return response