#!/usr/bin/env python3

"""
Utility for mirroring OpenShift 4 content.
"""

import json
import logging
import os
import subprocess
import sys
from urllib.error import URLError
from urllib.request import urlopen

from . import BASE_DIR
from .exceptions import ContainerRuntimeMissingError


logger = logging.getLogger(__name__)


class OpenShiftMirrorRuntime():
    """
    Runtime logic for containerized environment that can be used to run the
    tooling in this project.
    """

    def __init__(self, container_runtime=None):
        if container_runtime:
            self.container_runtime = container_runtime
        else:
            self.container_runtime = OpenShiftMirrorRuntime._container_runtime()

        self.container_image = 'localhost/openshift4-mirror:latest'

    @staticmethod
    def _container_runtime():
        """
        The container runtime to use.
        """
        for runtime in ['podman', 'docker']:
            try:
                subprocess.call([runtime, '--version'],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
                return runtime
            except OSError:
                pass

        raise ContainerRuntimeMissingError()

    def _build_container_if_needed(self):
        """
        Check if the container has been built and build it if not.
        """
        images = subprocess.check_output(
            [
                self.container_runtime,
                'images',
                self.container_image,
                '--format', 'json',
            ]
        )

        # If the list of images has a length of 0, then the image doesn't exist
        if len(json.loads(images)) == 0:
            logger.warning('The container does not exist %s',
                           self.container_image)

            # Check if we're in a connected environment and can build the iamge
            try:
                urlopen('https://api.openshift.com/', timeout=5)
            except URLError:
                logger.error('You are not connected to the internet.')
                logger.error('Please import the %s container and retry.',
                             self.container_image)
                sys.exit(1)

            logger.info('Building the container')
            self.build_container()
            logger.info('Finished building the container')

    def build_container(self):
        """
        Build the container image.
        """
        logger.info('Building the container image')

        subprocess.call([
            self.container_runtime,
            'build',
            '--tag', self.container_image,
            BASE_DIR,
        ])

        logger.info('Finished building the container image')

    def shell(self):
        """
        Open a shell in the container.
        """
        self._build_container_if_needed()

        logger.info('Starting shell in container')

        cmd = [
            self.container_runtime,
            'run',
            '--interactive',
            '--tty',
            '--rm',
            '--hostname', 'openshift4-mirror',
            '--security-opt', 'label=disable',
            '--volume', '{}:/app'.format(BASE_DIR),
        ]

        # Inject environment variables from host that are used for running the
        # automation
        for key, value in os.environ.items():
            if key.startswith('OPENSHIFT_MIRROR_'):
                cmd.extend(['--env', '{}={}'.format(key, value)])

        cmd.append(self.container_image)

        subprocess.call(cmd)
