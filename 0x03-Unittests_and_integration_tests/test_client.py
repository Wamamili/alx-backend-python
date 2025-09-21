#!/usr/bin/env python3
"""Unit tests for client.GithubOrgClient"""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Tests for GithubOrgClient"""

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

        with patch("client.get_json", return_value=test_payload) as mock_get_json:
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
                mock_get_json.assert_called_once_with(
                    "https://api.github.com/orgs/google/repos"
                )


if __name__ == "__main__":
    unittest.main()
