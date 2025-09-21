#!/usr/bin/env python3
"""Unit tests and integration tests for client.GithubOrgClient"""

import sys
import types
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class

# Provide a stub 'utils' module if it's missing so client.py can import it.
# This avoids ModuleNotFoundError during test collection.
if "utils" not in sys.modules:
    utils = types.ModuleType("utils")

    def get_json(url):
        import requests
        return requests.get(url).json()

    utils.get_json = get_json
    sys.modules["utils"] = utils

from client import GithubOrgClient
from fixtures import (
    org_payload,
    repos_payload,
    expected_repos,
    apache2_repos,
)


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the mocked payload"""
        expected = {"login": org_name}
        mock_get_json.return_value = expected

        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, expected)

        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    def test_public_repos_url(self):
        """Test that _public_repos_url returns the expected repos_url"""
        payload = {"repos_url": "https://api.github.com/orgs/google/repos"}

        with patch.object(
            GithubOrgClient, "org", new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = payload
            client = GithubOrgClient("google")

            self.assertEqual(client._public_repos_url, payload["repos_url"])
            mock_org.assert_called_once()

    def test_public_repos(self):
        """Test that public_repos returns expected list of repo names"""
        test_payload = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"},
        ]

        with patch("client.get_json", return_value=test_payload) as mock_json:
            with patch.object(
                GithubOrgClient,
                "_public_repos_url",
                new_callable=PropertyMock
            ) as mock_repos_url:
                mock_repos_url.return_value = (
                    "https://api.github.com/orgs/google/repos"
                )

                client = GithubOrgClient("google")
                result = client.public_repos()

                self.assertEqual(result, ["repo1", "repo2", "repo3"])
                mock_repos_url.assert_called_once()
                mock_json.assert_called_once_with(
                    "https://api.github.com/orgs/google/repos"
                )

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test that has_license returns True if repo license matches"""
        self.assertEqual(
            GithubOrgClient.has_license(repo, license_key),
            expected
        )


@parameterized_class([
    {
        "org_payload": org_payload,
        "repos_payload": repos_payload,
        "expected_repos": expected_repos,
        "apache2_repos": apache2_repos,
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos"""

    @classmethod
    def setUpClass(cls):
        """Start patcher for requests.get and mock API responses"""
        cls.get_patcher = patch("requests.get")
        mock_get = cls.get_patcher.start()

        def side_effect(url):
            if url.endswith("/orgs/google"):
                return MockResponse(cls.org_payload)
            if url.endswith("/orgs/google/repos"):
                return MockResponse(cls.repos_payload)
            return MockResponse(None)

        mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop patcher"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Integration test: public_repos returns expected repos"""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Integration test: public_repos filters repos by license"""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )


class MockResponse:
    """Simple mock response object for requests.get"""

    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


if __name__ == "__main__":
    unittest.main()
