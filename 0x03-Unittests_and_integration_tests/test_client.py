#!/usr/bin/env python3
"""
Unit tests for the client module.
"""
import unittest
from parameterized import parameterized, parameterized_class
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

    def public_repos(self, license=None):
        """
        Retrieves the list of public repositories.
        """
        repos = get_json(self._public_repos_url)
        if license:
            return [
                repo.get("name") for repo in repos
                if GithubOrgClient.has_license(repo, license)
            ]
        return [repo.get("name") for repo in repos]

    @staticmethod
    def has_license(repo: dict, license_key: str) -> bool:
        """
        Checks if a repository has a specific license.
        """
        license = repo.get("license", {})
        return license.get("key") == license_key


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
            repos_list = client.public_repos()

            self.assertEqual(repos_list, ["repo_a", "repo_b"])
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected_result):
        """
        Tests that has_license returns the correct boolean value.
        """
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected_result)


# Fixtures from fixtures.py (simulated for self-containment)
org_payload = {"repos_url": "https://api.github.com/orgs/google/repos"}
repos_payload = [
    {"name": "repo1"},
    {"name": "repo2"},
    {"name": "repo_a", "license": {"key": "apache-2.0"}},
    {"name": "repo_b", "license": {"key": "mit"}},
]
expected_repos = ["repo1", "repo2", "repo_a", "repo_b"]
apache2_repos = ["repo_a"]


@parameterized_class([
    {"org_payload": org_payload, "repos_payload": repos_payload,
     "expected_repos": expected_repos, "apache2_repos": apache2_repos}
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration test suite for the GithubOrgClient.public_repos method.
    """
    @classmethod
    def setUpClass(cls):
        """
        Sets up the test environment by mocking requests.get.
        """
        cls.get_patcher = patch('test_client.get_json')
        cls.mock_get_json = cls.get_patcher.start()

        def side_effect_func(url):
            if url == "https://api.github.com/orgs/google":
                return cls.org_payload
            elif url == cls.org_payload["repos_url"]:
                return cls.repos_payload
            return Mock()

        cls.mock_get_json.side_effect = side_effect_func

    @classmethod
    def tearDownClass(cls):
        """
        Tears down the test environment by stopping the patcher.
        """
        cls.get_patcher.stop()

    def test_public_repos(self):
        """
        Tests that public_repos returns the expected list of repos.
        """
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)
        self.assertEqual(self.mock_get_json.call_count, 2)

    def test_public_repos_with_license(self):
        """
        Tests that public_repos with a license argument returns the
        correct list of repos.
        """
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(license="apache-2.0"), self.apache2_repos)
        self.assertEqual(self.mock_get_json.call_count, 2)
