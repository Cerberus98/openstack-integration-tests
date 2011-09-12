import json
import os
import re

from kong import openstack
from kong import tests


class FlavorsTest(tests.FunctionalTest):
    def setUp(self):
        super(FlavorsTest, self).setUp()
        self.os = openstack.Manager(self.nova)

    def _index_flavors(self):
        url = '/flavors'
        response, body = self.os.nova.request('GET', url)
        self.assertEqual(response['status'], '200')
        body_dict = json.loads(body)
        self.assertEqual(body_dict.keys(), ['flavors'])
        return body_dict['flavors']

    def _show_flavor(self, flavor_id):
        url = '/flavors/%s' % flavor_id
        response, body = self.os.nova.request('GET', url)
        self.assertEqual(response['status'], '200')
        body_dict = json.loads(body)
        self.assertEqual(body_dict.keys(), ['flavor'])
        return body_dict['flavor']

    def _assert_flavor_entity_basic(self, flavor):
        actual_keys = set(flavor.keys())
        expected_keys = set(('id', 'name', 'links'))
        self.assertEqual(actual_keys, expected_keys)
        self._assert_flavor_links(flavor)

    def _assert_flavor_entity_detailed(self, flavor):
        actual_keys = set(flavor.keys())
        expected_keys = set(('id', 'name', 'ram', 'disk', 'links'))
        self.assertEqual(actual_keys, expected_keys)
        self.assertEqual(type(flavor['ram']), int)
        self.assertEqual(type(flavor['disk']), int)
        self._assert_flavor_links(flavor)

    def _assert_flavor_links(self, flavor):
        actual_links = flavor['links']

        flavor_id = str(flavor['id'])
        mgmt_url = self.os.nova.management_url
        bmk_url = re.sub(r'v1.1\/', r'', mgmt_url)

        self_link = os.path.join(mgmt_url, 'flavors', flavor_id)
        bookmark_link = os.path.join(bmk_url, 'flavors', flavor_id)

        expected_links = [
            {
                u'rel': u'self',
                u'href': unicode(self_link),
            },
            {
                u'rel': u'bookmark',
                u'href': unicode(bookmark_link),
            },
        ]

        self.assertEqual(actual_links, expected_links)

    @tests.tagged('nova', 'glance')
    def test_show_flavor(self):
        """Retrieve a single flavor"""

        flavors = self._index_flavors()

        for flavor in flavors:
            detailed_flavor = self._show_flavor(flavor['id'])
            self._assert_flavor_entity_detailed(detailed_flavor)

    @tests.tagged('nova', 'glance')
    def test_index_flavors_basic(self):
        """List all flavors"""

        flavors = self._index_flavors()

        for flavor in flavors:
            self._assert_flavor_entity_basic(flavor)

    @tests.tagged('nova', 'glance')
    def test_index_flavors_detailed(self):
        """List all flavors in detail"""

        url = '/flavors/detail'
        response, body = self.os.nova.request('GET', url)
        self.assertEqual(response['status'], '200')
        body_dict = json.loads(body)
        self.assertEqual(body_dict.keys(), ['flavors'])
        flavors = body_dict['flavors']

        for flavor in flavors:
            self._assert_flavor_entity_detailed(flavor)
