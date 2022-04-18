# Module of classes for interacting with CED Web API to fetch data.

import json
import warnings
from typing import List, Optional

import requests
from .network import requests_get


class CED:
    def __init__(self, server: str = 'ced.acc.jlab.org', ed: str = 'ced', workspace="OPS"):
        self.server = server
        self.ed = ed
        self.workspace = workspace
        self.url = f"https://{server}"

    def query_inventory(self, verify=True, **param_kwargs) -> dict:
        """Make a query to the CED's inventory end point.

        Args:
            verify:  Should the library attempt SSL verification of the CED web server.
            param_kwargs: All other key word arguments are passed on to the the get_query_params method
        """

        response = None
        url = self.url + "/inventory"
        params = self.get_query_params(**param_kwargs)
        try:
            response = requests_get(url, params, verify)

            data_dictionary = response.json()
            if data_dictionary['stat'] == 'ok':
                return data_dictionary['Inventory']['elements']
            else:
                raise RuntimeError(data_dictionary['message'])

        except json.JSONDecodeError:
            if response is not None:
                warnings.warn(f"Oops!  Invalid JSON response. Check request parameters and try again. "
                              f"\nresponse.url: {response.url}")
            warnings.warn(f"Oops!  Invalid JSON response. Check request parameters and try again.")
            raise  # rethrow the error
        except RuntimeError:
            if response is not None:
                warnings.warn(f"Response URL: {response.url}")
            raise

    def get_query_params(self, types: Optional[List[str]], name_nx: Optional[List[str]] = None,
                         name_ng: Optional[List[str]] = None, prop_Ex: Optional[List[str]] = None,
                         prop_Ea: Optional[List[str]] = None, date: Optional[List[str]] = None,
                         zone: Optional[List[str]] = None, properties: Optional[List[str]] = None,
                         sort: Optional[str] = None, repeat_multipass: Optional[bool] = None,
                         **kwargs) -> dict:
        """Generate a dictionary containing the query parameters to be used when making API call.

        Several well-known API options are included explicitly, with kwargs giving the option for more expert usage.

        Returns:
            A dictionary of parameters that are intended for consumption by the request package in making a CED query.
        """
        query = {'out': 'json', 'ced': self.ed, 'wrkspc': self.workspace, **kwargs}

        if properties is not None:
            query['p'] = properties
        if zone is not None:
            query['z'] = zone
        if types is not None:
            query['t'] = types
        if name_nx is not None:
            query['nx'] = name_nx
        if name_ng is not None:
            query['ng'] = name_ng
        if prop_Ex is not None:
            query['Ex'] = prop_Ex
        if prop_Ea is not None:
            query['Ea'] = prop_Ea
        if date is not None:
            query['d'] = date
        if sort is not None:
            query['s'] = sort
        if repeat_multipass is not None:
            if repeat_multipass:
                query['r'] = '1'

        return query


class TypeTree:
    """Class to query the CED Web API to obtain the types hierarchy"""

    # Instantiate the object
    def __init__(self, server: str = "ced.acc.jlab.org"):
        """Construct an instance of a TypeTree

        Args:
            server: The base URL for the API
        """
        self.url = f"https://{server}/api/catalog/type-tree"
        self.tree = {}

    # Retrieve Type tree data from the server and store it in self.tree
    def _populate_tree(self, verify: bool):
        # Set verify to False because of jlab MITM interference w/SSL
        response = requests.get(self.url, verify=verify)
        self.tree = response.json()

    # Receive notification of access to self.tree so that it can be populated
    # if necessary
    def _notify_access(self):
        if not self.tree:
            self._populate_tree()

    def is_a(self, type1, type2):
        """Answer if the type2 is a descendant (or identical) type as type1 based on CED hierarchy.

     Examples:
      is_a('IOC','IOC')        # true
      is_a('IOC','PC104')      # true
      is_a('Magnet','IPM1L02') # false

    Return: boolean
"""
        self._notify_access()
        found, lineage = self.lineage(type2)
        if not found:
            raise RuntimeError(type2 + " Not found in CED hierarchy.")
        else:
            # Be nice and do a case-insensitive comparison
            return type1.upper() in map(lambda x: x.upper(), lineage)

    # Return the list of CED Types in the hierarchy to which the specified type belongs
    #   type_name is the name of the CED Type whose lineage is being retrieved
    #   branch is the hierarchy being searched (defaults to entire tree)
    #   parents is the type_names ancestral to the branch being searched (defaults to empty list)
    #
    # Return (boolean, list)
    def lineage(self, type_name: str, branch: dict = None, parents: list = None):
        self._notify_access()
        # The default behavior is to search the entire tree
        if parents is None:
            parents = []
        if branch is None:
            branch = self.tree

        # Search for the type_name in the current branch by iterating through each top level item
        # in the branch.  When we encounter scalar items, they are leaf nodes and we test them to see
        # if they match the type_name we seek.  When we encounter dictionary items, they are sub-branches
        # and we must descend recursively into into them to continue searching.
        found = False
        lineage = parents.copy()
        for key, value in branch.items():
            lineage.append(key)
            if key.upper() == type_name.upper():
                found = True
            elif isinstance(value, dict):
                found, lineage = self.lineage(type_name, value, lineage)
            if found:
                break
            lineage = parents.copy()  # reset for next iteration
        return found, lineage
