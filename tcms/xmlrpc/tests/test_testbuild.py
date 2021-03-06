# -*- coding: utf-8 -*-


from xmlrpc.client import ProtocolError
from xmlrpc.client import Fault as XmlRPCFault

from tcms.tests.factories import ProductFactory
from tcms.tests.factories import TestBuildFactory
from tcms.tests.factories import TestCaseRunFactory
from tcms.tests.factories import TestRunFactory
from tcms.tests.factories import UserFactory
from tcms.tests.factories import VersionFactory
from tcms.xmlrpc.tests.utils import XmlrpcAPIBaseTest


class TestBuildCreate(XmlrpcAPIBaseTest):

    def _fixture_setup(self):
        super(TestBuildCreate, self)._fixture_setup()

        self.product = ProductFactory()

    def test_build_create_with_no_args(self):
        bad_args = ([], (), {})
        for arg in bad_args:
            with self.assertRaisesRegex(XmlRPCFault, 'Internal error:'):
                self.rpc_client.Build.create(arg)

    def test_build_create_with_no_perms(self):
        self.rpc_client.Auth.logout()
        with self.assertRaisesRegex(ProtocolError, '403 Forbidden'):
            self.rpc_client.Build.create({})

    def test_build_create_with_no_required_fields(self):
        values = {
            "description": "Test Build",
            "is_active": False
        }
        with self.assertRaisesRegex(XmlRPCFault, 'Product and name are both required'):
            self.rpc_client.Build.create(values)

        values["name"] = "TB"
        with self.assertRaisesRegex(XmlRPCFault, 'Product and name are both required'):
            self.rpc_client.Build.create(values)

        del values["name"]
        values["product"] = self.product.pk
        with self.assertRaisesRegex(XmlRPCFault, 'Product and name are both required'):
            self.rpc_client.Build.create(values)

    def test_build_create_with_illegal_fields(self):
        values = {
            "product": self.product.pk,
            "name": "B7",
            "milestone": "aaaaaaaa"
        }
        # various regex matching to account for version differences
        # between SQLite (different versions), MySQL and Postgres
        with self.assertRaisesRegex(
                XmlRPCFault,
                ".*(may not be NULL|NOT NULL constraint|violates not-null|cannot be null).*"):
            self.rpc_client.Build.create(values)

    def test_build_create_with_non_existing_product(self):
        values = {
            "product": 9999,
            "name": "B7",
            "description": "Test Build",
            "is_active": False
        }
        with self.assertRaisesRegex(XmlRPCFault, 'Product matching query does not exist'):
            self.rpc_client.Build.create(values)

        values['product'] = "AAAAAAAAAA"
        with self.assertRaisesRegex(XmlRPCFault, 'Product matching query does not exist'):
            self.rpc_client.Build.create(values)

    def test_build_create_with_chinese(self):
        values = {
            "product": self.product.pk,
            "name": "B99",
            "description": "开源中国",
            "is_active": False
        }
        b = self.rpc_client.Build.create(values)
        self.assertIsNotNone(b)
        self.assertEqual(b['product_id'], self.product.pk)
        self.assertEqual(b['name'], "B99")
        self.assertEqual(b['description'], values['description'])
        self.assertEqual(b['is_active'], False)

    def test_build_create(self):
        values = {
            "product": self.product.pk,
            "name": "B7",
            "description": "Test Build",
            "is_active": False
        }
        b = self.rpc_client.Build.create(values)
        self.assertIsNotNone(b)
        self.assertEqual(b['product_id'], self.product.pk)
        self.assertEqual(b['name'], "B7")
        self.assertEqual(b['description'], "Test Build")
        self.assertEqual(b['is_active'], False)


class TestBuildUpdate(XmlrpcAPIBaseTest):

    def _fixture_setup(self):
        super(TestBuildUpdate, self)._fixture_setup()

        self.product = ProductFactory()
        self.another_product = ProductFactory()

        self.build_1 = TestBuildFactory(product=self.product)
        self.build_2 = TestBuildFactory(product=self.product)
        self.build_3 = TestBuildFactory(product=self.product)

    def test_build_update_with_non_existing_build(self):
        with self.assertRaisesRegex(XmlRPCFault, 'TestBuild matching query does not exist'):
            self.rpc_client.Build.update(-99, {})

    def test_build_update_with_no_perms(self):
        self.rpc_client.Auth.logout()
        with self.assertRaisesRegex(ProtocolError, '403 Forbidden'):
            self.rpc_client.Build.update(self.build_1.pk, {})

    def test_build_update_with_multi_id(self):
        builds = (self.build_1.pk, self.build_2.pk, self.build_3.pk)
        with self.assertRaisesRegex(XmlRPCFault, 'Invalid parameter'):
            self.rpc_client.Build.update(builds, {})

    def test_build_update_with_non_existing_product_id(self):
        with self.assertRaisesRegex(XmlRPCFault, 'Product matching query does not exist'):
            self.rpc_client.Build.update(self.build_1.pk, {"product": -9999})

    def test_build_update_with_non_existing_product_name(self):
        with self.assertRaisesRegex(XmlRPCFault, 'Product matching query does not exist'):
            self.rpc_client.Build.update(self.build_1.pk, {"product": "AAAAAAAAAAAAAA"})

    def test_build_update(self):
        b = self.rpc_client.Build.update(self.build_3.pk, {
            "product": self.another_product.pk,
            "name": "Update",
            "description": "Update from unittest."
        })
        self.assertIsNotNone(b)
        self.assertEqual(b['product_id'], self.another_product.pk)
        self.assertEqual(b['name'], 'Update')
        self.assertEqual(b['description'], 'Update from unittest.')


class TestBuildGet(XmlrpcAPIBaseTest):

    def _fixture_setup(self):
        super(TestBuildGet, self)._fixture_setup()

        self.product = ProductFactory()
        self.build = TestBuildFactory(description='for testing', product=self.product)

    def test_build_get_with_no_args(self):
        bad_args = ([], (), {})
        for arg in bad_args:
            with self.assertRaisesRegex(XmlRPCFault, 'Invalid parameter'):
                self.rpc_client.Build.get(arg)

    def test_build_get_with_non_exist_id(self):
        with self.assertRaisesRegex(XmlRPCFault, 'TestBuild matching query does not exist'):
            self.rpc_client.Build.get(-9999)

    def test_build_get_with_id(self):
        b = self.rpc_client.Build.get(self.build.pk)
        self.assertIsNotNone(b)
        self.assertEqual(b['build_id'], self.build.pk)
        self.assertEqual(b['name'], self.build.name)
        self.assertEqual(b['product_id'], self.product.pk)
        self.assertEqual(b['description'], 'for testing')
        self.assertTrue(b['is_active'])


class TestBuildGetCaseRuns(XmlrpcAPIBaseTest):

    def _fixture_setup(self):
        super(TestBuildGetCaseRuns, self)._fixture_setup()

        self.product = ProductFactory()
        self.build = TestBuildFactory(product=self.product)
        self.user = UserFactory()
        self.case_run_1 = TestCaseRunFactory(assignee=self.user, build=self.build)
        self.case_run_2 = TestCaseRunFactory(assignee=self.user, build=self.build)

    def test_build_get_with_no_args(self):
        bad_args = ([], (), {})
        for arg in bad_args:
            with self.assertRaisesRegex(XmlRPCFault, 'Invalid parameter'):
                self.rpc_client.Build.get_caseruns(arg)

    def test_build_get_with_non_exist_id(self):
        with self.assertRaisesRegex(XmlRPCFault, 'TestBuild matching query does not exist'):
            self.rpc_client.Build.get_caseruns(-9999)

    def test_build_get_with_id(self):
        b = self.rpc_client.Build.get_caseruns(self.build.pk)
        self.assertIsNotNone(b)
        self.assertEqual(2, len(b))
        self.assertEqual(b[0]['case'], self.case_run_1.case.summary)


class TestBuildGetRuns(XmlrpcAPIBaseTest):

    def _fixture_setup(self):
        super(TestBuildGetRuns, self)._fixture_setup()

        self.product = ProductFactory()
        self.version = VersionFactory(value='0.1', product=self.product)
        self.build = TestBuildFactory(product=self.product)
        self.user = UserFactory()
        self.test_run = TestRunFactory(manager=self.user, default_tester=None,
                                       build=self.build)

    def test_build_get_with_no_args(self):
        bad_args = ([], (), {})
        for arg in bad_args:
            with self.assertRaisesRegex(XmlRPCFault, 'Invalid parameter'):
                self.rpc_client.Build.get_runs(arg)

    def test_build_get_with_non_exist_id(self):
        with self.assertRaisesRegex(XmlRPCFault, 'TestBuild matching query does not exist'):
            self.rpc_client.Build.get_runs(-9999)

    def test_build_get_with_id(self):
        b = self.rpc_client.Build.get_runs(self.build.pk)
        self.assertIsNotNone(b)
        self.assertEqual(len(b), 1)
        self.assertEqual(b[0]['summary'], self.test_run.summary)


class TestBuildCheck(XmlrpcAPIBaseTest):

    def _fixture_setup(self):
        super(TestBuildCheck, self)._fixture_setup()

        self.product = ProductFactory()
        self.build = TestBuildFactory(description='testing ...', product=self.product)

    def test_check_build_with_no_args(self):
        bad_args = (None, [], (), {}, "")
        for arg in bad_args:
            with self.assertRaisesRegex(XmlRPCFault, 'TestBuild matching query does not exist'):
                self.rpc_client.Build.check_build(arg, self.product.pk)

            with self.assertRaisesRegex(XmlRPCFault, 'Internal error:'):
                self.rpc_client.Build.check_build("B5", arg)

    def test_check_build_with_non_exist_build_name(self):
        with self.assertRaisesRegex(XmlRPCFault, 'TestBuild matching query does not exist'):
            self.rpc_client.Build.check_build("AAAAAAAAAAAAAA", self.product.pk)

    def test_check_build_with_non_exist_product_id(self):
        with self.assertRaisesRegex(XmlRPCFault, 'Product matching query does not exist'):
            self.rpc_client.Build.check_build("B5", -9)

    def test_check_build_with_non_exist_product_name(self):
        with self.assertRaisesRegex(XmlRPCFault, 'Product matching query does not exist'):
            self.rpc_client.Build.check_build("B5", "AAAAAAAAAAAAAAAA")

    def test_check_build(self):
        b = self.rpc_client.Build.check_build(self.build.name, self.product.pk)
        self.assertIsNotNone(b)
        self.assertEqual(b['build_id'], self.build.pk)
        self.assertEqual(b['name'], self.build.name)
        self.assertEqual(b['product_id'], self.product.pk)
        self.assertEqual(b['description'], 'testing ...')
        self.assertEqual(b['is_active'], True)
