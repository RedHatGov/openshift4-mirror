#!/usr/bin/env python3

"""
Utility for mirroring OpenShift 4 content.
"""

class ContainerRuntimeMissingError(Exception):
    """
    Exception for missing container runtime.
    """


class MissingOpenShiftVersionError(Exception):
    """
    Exception for missing OpenShift version.
    """

class InvalidOpenShiftPlatformError(Exception):
    """
    Exception for invalid OpenShift platform.
    """

class NonSemanticVersionUsedError(Exception):
    """
    Exception for using non-semantically versioned release name. Use a numbered release.
    """