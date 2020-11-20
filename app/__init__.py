#!/usr/bin/env python3
# pylint: disable=R0903

"""
Utility for mirroring OpenShift 4 content.
"""

import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class OpenShiftMirrorBase():
    """
    Base class for OpenShift mirror utility.
    """

    def __init__(self, openshift_version):
        self.openshift_version = openshift_version

    def openshift_version_minor(self):
        """
        Parse the OpenShift version to get the minor version (e.g. 4.5)
        """
        version_parts = self.openshift_version.split('.')
        return '{}.{}'.format(version_parts[0], version_parts[1])
