"""Tests for API utilities."""

from unittest.mock import Mock, patch

import pytest

from jst_django.exceptions import APIError, VersionError
from jst_django.utils.api import Github


class TestGithub:
    """Test Github API client."""

    @pytest.fixture
    def github_client(self):
        """Create Github client."""
        return Github(repo="test-repo", owner="test-owner")

    def test_init(self, github_client):
        """Test Github client initialization."""
        assert github_client.repo == "test-repo"
        assert github_client.owner == "test-owner"
        assert "repos/test-owner/test-repo" in github_client.base_url

    @patch("requests.request")
    def test_request_success(self, mock_request, github_client):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_request.return_value = mock_response

        result = github_client.request("test-endpoint")
        assert result == {"data": "test"}

    @patch("requests.request")
    def test_request_not_found(self, mock_request, github_client):
        """Test 404 error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response

        with pytest.raises(APIError):
            github_client.request("test-endpoint")

    @patch("requests.request")
    def test_request_rate_limit(self, mock_request, github_client):
        """Test rate limit error."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_request.return_value = mock_response

        with pytest.raises(APIError):
            github_client.request("test-endpoint")

    @patch.object(Github, "request")
    def test_releases(self, mock_request, github_client):
        """Test getting releases."""
        mock_request.return_value = [
            {"name": "v1.0.0"},
            {"name": "v1.1.0"},
        ]

        releases = github_client.releases()
        assert releases == ["v1.0.0", "v1.1.0"]

    @patch.object(Github, "request")
    def test_latest_release(self, mock_request, github_client):
        """Test getting latest release."""
        mock_request.return_value = {"name": "v1.2.0"}

        version = github_client.latest_release()
        assert version == "v1.2.0"

    @patch.object(Github, "request")
    def test_get_commit_id(self, mock_request, github_client):
        """Test getting commit ID."""
        mock_request.return_value = {"object": {"sha": "abc123"}}

        commit_id = github_client.get_commit_id("v1.0.0")
        assert commit_id == "abc123"

    def test_check_version_valid(self, github_client):
        """Test version validation with valid version."""
        versions = ["v1.0.0", "v1.1.0", "v1.2.0"]
        assert github_client.check_version("v1.1.0", versions) is True

    def test_check_version_invalid(self, github_client):
        """Test version validation with invalid version."""
        versions = ["v1.0.0", "v1.1.0"]
        with pytest.raises(VersionError):
            github_client.check_version("v2.0.0", versions)
