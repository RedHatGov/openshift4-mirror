#!/usr/bin/env python3

"""
Utility for mirroring OpenShift 4 content.
"""

import json
import logging
import os
import re
import subprocess
import tarfile

import requests

from . import OpenShiftMirrorBase, BASE_DIR
from .exceptions import NonSemanticVersionUsedError


logger = logging.getLogger(__name__)


class OpenShiftMirrorBundle(OpenShiftMirrorBase):
    """
    Bundle logic for downloading necessary content and packaging it.
    """

    def __init__(self, openshift_version, pull_secret, platform=None,
                 catalogs=None, bundle_dir=None, skip_existing=False,
                 skip_release=False, skip_catalogs=False, skip_rhcos=False):
        super().__init__(openshift_version)
        self.platform = platform
        self.skip_existing = skip_existing
        self.skip_release = skip_release
        self.skip_catalogs = skip_catalogs
        self.skip_rhcos = skip_rhcos
        self._check_version(self.openshift_version)
        if bundle_dir:
            self.bundle_dir = os.path.join(bundle_dir, self.openshift_version)
        else:
            self.bundle_dir = os.path.join(
                BASE_DIR, 'bundle', self.openshift_version)
       
        self.bundle_dirs = {
            'bin': os.path.join(self.bundle_dir, 'bin'),
            'release': os.path.join(self.bundle_dir, 'release'),
            'rhcos': os.path.join(self.bundle_dir, 'rhcos'),
            'catalogs': os.path.join(self.bundle_dir, 'catalogs'),
            'clients': os.path.join(self.bundle_dir, 'clients'),
        }
        self._create_dir_structure()

        self.pull_secret = pull_secret
        self.pull_secret_path = self._save_pull_secret()

        self.catalog_indexes = {
            'redhat-operators': 'registry.redhat.io/redhat/redhat-operator-index:v{}'.format(self.openshift_version_minor()),
            'certified-operators': 'registry.redhat.io/redhat/certified-operator-index:v{}'.format(self.openshift_version_minor()),
            'redhat-marketplace': 'registry.redhat.io/redhat/redhat-marketplace-index:v{}'.format(self.openshift_version_minor()),
            'community-operators': 'registry.redhat.io/redhat/community-operator-index:latest',
        }
        if catalogs is None:
            logger.debug('Setting catalogs to all %s',
                         ', '.join(self.catalog_indexes.keys()))
            self.catalogs = self.catalog_indexes.keys()
        else:
            self.catalogs = catalogs

        self.clients_base_url = [
            'https://mirror.openshift.com/pub/openshift-v4/clients/ocp',
            'https://mirror.openshift.com/pub/openshift-v4/clients/ocp-dev-preview'
        ]

    def _create_dir_structure(self):
        """
        Create directory structure for bundle.
        """
        for i in self.bundle_dirs.values():
            logger.info('Creating directory %s', i)
            os.makedirs(i, exist_ok=True)

    def _save_pull_secret(self):
        """
        Save pull secret to disk and return it's path.
        """
        pull_secret_path = os.path.join(
            self.bundle_dir,
            'pull-secret.json',
        )

        self.pull_secret_path = pull_secret_path

        logger.info('Saving pull secret to %s', pull_secret_path)

        with open(pull_secret_path, 'w') as f:
            json.dump(json.loads(self.pull_secret), f)

        return pull_secret_path

    def _check_version(self, openshift_version):
        """
        Check for semantic versioning
        """
        if self.openshift_version == 'latest' or self.openshift_version == 'stable' or self.openshift_version == 'fast':
            raise NonSemanticVersionUsedError


    def _download_client(self, filename, files_to_extract=None):
        """
        Download the client with the given filename.
        """

        def _get_url():
            for url in self.clients_base_url:
                r = requests.get('/'.join([url, self.openshift_version]))
                if r.status_code == 200:
                    return url

        download_url = '/'.join([
            _get_url(),
            self.openshift_version,
            filename,
        ])
        output_path = os.path.join(
            self.bundle_dirs['clients'],
            filename,
        )

        if self.skip_existing and os.path.exists(output_path):
            logger.info('Found existing file %s, skipping download of %s',
                        output_path, download_url)
            return

        logger.info('Downloading %s', download_url)
        r = requests.get(download_url)
        logger.info('Finished downloading %s', download_url)

        with open(output_path, 'wb') as f:
            logger.info('Saving %s to %s', download_url, output_path)
            f.write(r.content)

        if files_to_extract:
            with tarfile.open(output_path) as tar:
                for i in files_to_extract:
                    logger.info('Extracting %s from %s', i, output_path)
                    tar.extract(i, path=self.bundle_dirs['bin'])
    
    def download_clients(self):
        """
        Download the OpenShift installer and client binaries.
        """
        logger.info('Starting client download')

        self._download_client('openshift-install-linux.tar.gz',
                              files_to_extract=['openshift-install'])
        self._download_client('openshift-client-linux.tar.gz',
                              files_to_extract=['oc', 'kubectl'])
        self._download_client('sha256sum.txt')

        logger.info('Finished client download')

    def download_rhcos(self):
        """
        Download the RHCOS image for the given platform.
        """
        minor = re.search('4\.\d\.\d', self.openshift_version).group(0)

        manifest = 'https://raw.githubusercontent.com/openshift/installer/release-{}/data/data/rhcos.json'.format(minor[0:3])

        j = json.loads(requests.get(manifest).content)
        rhcos_base_url = j['baseURI']
        filename = j['images']['{}'.format(self.platform)]['path']

        logger.info('Starting RHCOS download')

        download_url = ''.join([
            rhcos_base_url,
            filename,
        ])
        output_path = os.path.join(
            self.bundle_dirs['rhcos'],
            filename,
        )

        if self.skip_existing and os.path.exists(output_path):
            logger.info('Found existing file %s, skipping download of %s',
                        output_path, download_url)
        else:
            logger.info('Downloading %s', download_url)
            r = requests.get(download_url)
            logger.info('Finished downloading %s', download_url)

            with open(output_path, 'wb') as f:
                logger.info('Saving %s to %s', download_url, output_path)
                f.write(r.content)

        logger.info('Finished RHCOS download')

    def download_release(self):
        """
        Download Openshift release content.
        """
        logger.info('Starting release download')

        output_path = os.path.join(self.bundle_dirs['release'], 'v2')
        if self.skip_existing and os.path.exists(output_path):
            logger.info('Found existing release content, skipping download')
        else:
            subprocess.call([
                os.path.join(self.bundle_dirs['bin'], 'oc'),
                'adm',
                'release',
                'mirror',
                '--registry-config', self.pull_secret_path,
                '--to-dir', self.bundle_dirs['release'],
                self.openshift_version,
            ])

        logger.info('Finished release download')

    def download_catalogs(self):
        """
        Download OpenShift catalogs content.
        """
        logger.info('Starting catalogs download')

        for catalog in self.catalogs:
            output_dir = os.path.join(self.bundle_dirs['catalogs'], catalog)

            if self.skip_existing and os.path.exists(output_dir):
                logger.info('Found existing catalog at %s, skipping download',
                            output_dir)
                continue

            os.makedirs(output_dir, exist_ok=True)

            logger.info('Mirroring catalog manifests for %s from %s',
                        catalog, self.catalog_indexes[catalog])

            subprocess.call([
                os.path.join(self.bundle_dirs['bin'], 'oc'),
                'adm',
                'catalog',
                'mirror',
                '--registry-config', self.pull_secret_path,
                '--manifests-only',
                '--to-manifests', output_dir,
                self.catalog_indexes[catalog],
                'dummyregistry.example',
            ])

            with open(os.path.join(output_dir, 'mapping.txt')) as f:
                mapping_data = f.read()

            with open(os.path.join(output_dir, 'mapping.local.txt'), 'w') as f:
                f.write(
                    re.sub('dummyregistry.example/', 'file://', mapping_data)
                )

            logger.info('Mirroring catalog images for %s', catalog)

            subprocess.call([
                os.path.join(self.bundle_dirs['bin'], 'oc'),
                'image',
                'mirror',
                '--registry-config', self.pull_secret_path,
                '--dir', output_dir,
                '--filter-by-os', 'linux/amd64',
                '--continue-on-error=true',
                '--filename', os.path.join(output_dir, 'mapping.local.txt'),
            ])

        logger.info('Finished catalogs download')

    def delete_pull_secret(self):
        """
        Remove pull secret from bundle
        """
        if os.path.exists(self.pull_secret_path):
            os.remove(self.pull_secret_path)

    def bundle(self):
        """
        Download and package mirrored content.
        """
        self.download_clients()

        if not self.skip_release:
            self.download_release()

        if not self.skip_catalogs:
            self.download_catalogs()

        if not self.skip_rhcos:
            self.download_rhcos()
