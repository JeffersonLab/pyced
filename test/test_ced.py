# File containing some tests of the ced module.

from pyced.ced import TypeTree, CED
import json
import unittest
from unittest import TestCase


class TestTypeTree(TestCase):

    def test_is_a(self):
        # We load hierarchy expected from CED web server from a json file instead
        # and then make our assertions based on it.
        # read file
        with open('test/tree.json', 'r') as tree_file:
            data = tree_file.read()
        tree = TypeTree()
        tree.tree = json.loads(data)  # parses file into dict

        self.assertTrue(tree.is_a('Magnet', 'Quad'))
        self.assertFalse(tree.is_a('IOC', 'Dipole'))


class TestCED(TestCase):

    # Verify the inventory constructor properly incorporates extra_properties parameter
    def test_get_query_params(self):
        ced = CED()
        params = ced.get_query_params(zone=['Injector'], types=['Quad'], properties=['Housed_by', 'S', 'EPICSName'])

        # inventory = Inventory('Injector', ['Quad'], ['Housed_by', 'S'])
        # Our extra property should be present
        self.assertListEqual(['Housed_by', 'S', 'EPICSName'], params['p'])
        self.assertListEqual(['Injector'], params['z'])
        self.assertEqual('OPS', params['wrkspc'])

    def test_query_inventory(self):
        ced = CED()
        elems = ced.query_inventory(types=['CryoCavity'], properties=['CavityType', 'EPICSName'],
                                    name_nx=['1L0[24]-1'], prop_Ex=["CavityType='C25'"])

        exp = [{"type": "CryoCavity", "name": "1L02-1", "properties": {"CavityType": "C25", "EPICSName": "R121"}}]
        self.assertEqual(exp[0]['type'], elems[0]['type'])
        self.assertEqual(exp[0]['name'], elems[0]['name'])
        self.assertDictEqual(exp[0]['properties'], elems[0]['properties'])


if __name__ == '__main__':
    unittest.main()
