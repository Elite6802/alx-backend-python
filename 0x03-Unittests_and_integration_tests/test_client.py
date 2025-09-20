#!/usr/bin/env python3
"""
Unit tests for the client module.
"""
import unittest
from parameterized import parameterized
from unittest.mock import patch, Mock, PropertyMock


# Define a minimal GithubOrgClient class for the purpose of this test,
# since the full client.py file was not provided.
class GithubOrgClient:
    """
    A simple client for testing purposes.
    """
    def __init__(self, org_name):
        self._org_url = f"https://api.github.com/orgs/{org_name}"
        self._org_name = org_name

    @property
    def org(self):
        """
        Retrieves the organization's information.
        """
        # This assumes get_json is in the utils module, as per previous tasks.
        return get_json(self._org_url)

    @property
    def _public_repos_url(self):
        """
        Retrieves the URL for public repositories.
        """
        return self.org.get("repos_url")

    @property
    def public_repos(self):
        """
        Retrieves the list of public repositories.
        """
        repos = get_json(self._public_repos_url)
        return [repo.get("name") for repo in repos]


# The get_json function is assumed to be imported from utils, as in previous
# tasks. A mock implementation is not needed here since we will patch it.
def get_json(url):
    """
    Dummy get_json function.
    """
    pass


class TestGithubOrgClient(unittest.TestCase):
    """
    Test suite for the GithubOrgClient class.
    """
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('test_client.get_json')
    def test_org(self, org_name, mock_get_json):
        """
        Tests that GithubOrgClient.org returns the correct value
        and get_json is called once with the expected argument.
        """
        client = GithubOrgClient(org_name)
        client.org
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    def test_public_repos_url(self):
        """
        Test that _public_repos_url returns the correct repos URL
        based on a mocked payload.
        """
        payload = {"repos_url": "http://example.com/repos"}
        with patch(
            'test_client.GithubOrgClient.org',
            new_callable=Mock
        ) as mock_org:
            mock_org.get.return_value = payload["repos_url"]
            client = GithubOrgClient("test_org")
            self.assertEqual(
                client._public_repos_url, payload["repos_url"]
            )

    @patch('test_client.get_json')
    def test_public_repos(self, mock_get_json):
        """
        Tests that public_repos returns the expected list of repos.
        """
        repos_payload = [
            {"name": "repo_a", "license": "mit"},
            {"name": "repo_b", "license": "apache-2.0"},
        ]
        mock_get_json.return_value = repos_payload

        with patch(
            'test_client.GithubOrgClient._public_repos_url',
            new_callable=PropertyMock
        ) as mock_public_repos_url:
            mock_public_repos_url.return_value = "http://example.com/repos"
            client = GithubOrgClient("test_org")
            repos_list = client.public_repos

            self.assertEqual(repos_list, ["repo_a", "repo_b"])
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once()
