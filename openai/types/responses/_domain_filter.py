# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import fnmatch
from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["DomainFilter"]


def matches_domain_pattern(pattern: str, domain: str) -> bool:
    """
    Check if a domain matches a given pattern with support for subdomains and wildcards.

    Supports:
    - Exact matches: "example.com"
    - Subdomain matches: pattern "github.com" matches "api.github.com"
    - Wildcard patterns: "*.edu", "*.gov.uk", "*.github.com"
    - Case-insensitive matching

    Args:
        pattern: The domain pattern to match against (e.g., "github.com", "*.edu")
        domain: The domain to check (e.g., "api.github.com")

    Returns:
        True if the domain matches the pattern, False otherwise.
    """
    # Normalize: strip whitespace and convert to lowercase
    pattern = pattern.strip().lower()
    domain = domain.strip().lower()

    # Empty inputs are not valid
    if not pattern or not domain:
        return False

    # Handle exact match case first
    if pattern == domain:
        return True

    # Handle wildcard patterns using fnmatch
    # fnmatch supports * and ? wildcards
    if "*" in pattern or "?" in pattern:
        return fnmatch.fnmatch(domain, pattern)

    # Handle subdomain matching
    # If pattern is "github.com" and domain is "api.github.com",
    # check if domain ends with the pattern (preceded by a dot)
    if domain.endswith("." + pattern):
        return True

    return False


class DomainFilter(BaseModel):
    """Configuration for filtering domains in web search results."""

    allowed_domains: Optional[list[str]] = None
    """
    List of domains to allow in search results.
    If specified, only these domains (and their subdomains) will be included.
    Supports wildcards like "*.edu" or "*.github.com".
    """

    blocked_domains: Optional[list[str]] = None
    """
    List of domains to block from search results.
    If a domain matches any pattern in this list, it will be excluded.
    Supports wildcards like "*.example.com".
    Blocked domains take precedence over allowed domains.
    """

    def should_include_domain(self, domain: str) -> bool:
        """
        Determine if a domain should be included based on filter rules.

        Blocked domains take precedence over allowed domains.

        Args:
            domain: The domain to check

        Returns:
            True if the domain should be included, False if it should be blocked.
        """
        # Strip whitespace and normalize
        domain = domain.strip()
        if not domain:
            return False

        # Check blocked list first (higher priority)
        if self.blocked_domains:
            for blocked_pattern in self.blocked_domains:
                if matches_domain_pattern(blocked_pattern, domain):
                    return False

        # Check allowed list (if empty, allow by default)
        if self.allowed_domains:
            for allowed_pattern in self.allowed_domains:
                if matches_domain_pattern(allowed_pattern, domain):
                    return True
            # If allowed list is specified and domain doesn't match, block it
            return False

        # If no allowed list specified and not blocked, allow by default
        return True
