"""GitHub API utilities for jst-django."""

from typing import List, Optional, Union

import requests

from jst_django.exceptions import APIError, VersionError
from jst_django.utils.logger import logger


class Github:
    """GitHub API client for repository operations."""

    def __init__(self, repo: str = "django", owner: str = "JscorpTech") -> None:
        """
        Initialize GitHub API client.

        Args:
            repo: Repository name
            owner: Repository owner
        """
        self.owner = owner
        self.repo = repo
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"
        self.release_urls = {
            "list": "releases",
            "latest": "releases/latest",
            "detail": "releases/tags/{}",
            "ref": "git/refs/tags/{}",
        }
        self.timeout = 30  # seconds

    def request(self, action: str, method: str = "GET") -> Union[dict, list]:
        """
        Make request to GitHub API.

        Args:
            action: API action/endpoint
            method: HTTP method

        Returns:
            API response data

        Raises:
            APIError: If request fails
        """
        url = f"{self.base_url}/{action}"

        try:
            logger.debug(f"Making {method} request to: {url}")
            response = requests.request(method, url, timeout=self.timeout)

            if response.status_code == 200:
                return response.json()

            # Handle specific error codes
            if response.status_code == 404:
                raise APIError(f"Resource not found: {url}")
            elif response.status_code == 403:
                raise APIError("API rate limit exceeded or access forbidden")
            elif response.status_code >= 500:
                raise APIError(f"GitHub server error: {response.status_code}")
            else:
                raise APIError(
                    f"API request failed with status {response.status_code}",
                    details=response.text,
                )

        except requests.exceptions.Timeout:
            raise APIError(f"Request timeout after {self.timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise APIError("Failed to connect to GitHub API. Check your internet connection.")
        except requests.exceptions.RequestException as e:
            raise APIError("API request failed", details=str(e))

    def releases(self, version: Optional[str] = None) -> Union[List[str], bool]:
        """
        Get all releases or check if specific version exists.

        Args:
            version: Optional version to check

        Returns:
            List of versions or validation result

        Raises:
            APIError: If request fails
            VersionError: If version not found
        """
        try:
            logger.info("Fetching releases from GitHub")
            releases_data = self.request(self.release_urls["list"])
            versions = [release["name"] for release in releases_data]

            if version:
                return self.check_version(version, versions)

            logger.info(f"Found {len(versions)} releases")
            return versions

        except Exception as e:
            logger.exception("Failed to fetch releases")
            raise

    def latest_release(self) -> str:
        """
        Get latest release version.

        Returns:
            Latest release version string

        Raises:
            APIError: If request fails
        """
        try:
            logger.info("Fetching latest release")
            release_data = self.request(self.release_urls["latest"])
            version = release_data["name"]
            logger.info(f"Latest release: {version}")
            return version

        except Exception as e:
            logger.exception("Failed to fetch latest release")
            raise APIError("Failed to fetch latest release", details=str(e))

    def get_commit_id(self, version: str) -> str:
        """
        Get commit SHA for a specific version tag.

        Args:
            version: Version tag

        Returns:
            Commit SHA

        Raises:
            APIError: If request fails
        """
        try:
            logger.debug(f"Fetching commit ID for version: {version}")
            ref_data = self.request(self.release_urls["ref"].format(version))
            commit_sha = ref_data["object"]["sha"]
            logger.debug(f"Commit SHA: {commit_sha}")
            return commit_sha

        except Exception as e:
            logger.exception(f"Failed to get commit ID for version: {version}")
            raise APIError(f"Failed to get commit ID for version: {version}", details=str(e))

    def check_version(self, version: str, versions: List[str]) -> bool:
        """
        Check if version exists in available versions.

        Args:
            version: Version to check
            versions: List of available versions

        Returns:
            True if version exists

        Raises:
            VersionError: If version not found
        """
        if version not in versions:
            available = ", ".join(versions[:10])  # Show first 10
            logger.error(f"Version {version} not found")
            raise VersionError(
                f"Version '{version}' not found",
                details=f"Available versions: {available}{'...' if len(versions) > 10 else ''}",
            )

        logger.info(f"Version {version} found")
        return True

    def branches(self) -> List[str]:
        """
        Get filtered list of branches.

        Returns:
            List of branch names

        Raises:
            APIError: If request fails
        """
        try:
            logger.info("Fetching branches")
            branches_data = self.request("branches")
            all_branches = [branch["name"] for branch in branches_data]

            # Filter relevant branches
            filtered_branches = []
            for branch in all_branches:
                if branch.startswith("V") or branch in ["main", "dev"]:
                    filtered_branches.append(branch)

            filtered_branches.reverse()
            logger.info(f"Found {len(filtered_branches)} relevant branches")
            return filtered_branches

        except Exception as e:
            logger.exception("Failed to fetch branches")
            raise APIError("Failed to fetch branches", details=str(e))
