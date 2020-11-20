#!/usr/bin/env python3

"""
Utility for mirroring OpenShift 4 content.
"""

import argparse
import logging
import sys


logger = logging.getLogger(__name__)


class CLI():
    """
    CLI built using argparse to enable interaction with the application.
    """

    def __init__(self):
        logger.debug('Instantiating CLI')

        self.parser = argparse.ArgumentParser(
            description='Utility for mirroring OpenShift 4 content.'
        )
        self.subparsers = self.parser.add_subparsers()
        self.parent_parser = CLI._parent_parser()

        self.add_subparser_bundle()
        self.add_subparser_build()
        self.add_subparser_shell()

    @staticmethod
    def _parent_parser():
        """
        Create parent subparser that contains common parameters for parsersfdsafdsafsd
        that inherit it.
        """
        parser = argparse.ArgumentParser(add_help=False)

        parser.add_argument(
            '--openshift-version',
            required=True,
            help='the OpenShift version (e.g. 4.5.11)'
        )

        return parser

    def add_subparser(self, name, parser_help='', parents=[]):
        """
        Add a subparser that inherits the parent subparser.
        """
        logger.debug('Adding subparser %s', name)

        parser = self.subparsers.add_parser(
            name,
            parents=parents,
            help=parser_help
        )
        parser.set_defaults(action=name)
        return parser

    def add_subparser_build(self):
        """
        Add subparser for build.
        """
        parser = self.add_subparser(
            'build',
            parser_help='build the container image',
        )

        parser.add_argument(
            '--container-runtime',
            choices=[
                'podman',
                'docker',
            ],
            help='override the container runtime to use'
        )

    def add_subparser_shell(self):
        """
        Add subparser for shell.
        """
        parser = self.add_subparser(
            'shell',
            parser_help='open a shell in the container environment',
        )

        parser.add_argument(
            '--container-runtime',
            choices=[
                'podman',
                'docker',
            ],
            help='override the container runtime to use'
        )

    def add_subparser_bundle(self):
        """
        Add subparser for bundle.
        """
        parser = self.add_subparser(
            'bundle',
            parser_help='bundle the OpenShift content',
            parents=[self.parent_parser],
        )

        parser.add_argument(
            '--pull-secret',
            required=True,
            help=('the content of your pull secret (can be found at '
                  'https://cloud.redhat.com/openshift/install/pull-secret)')
        )
        parser.add_argument(
            '--platform',
            required=True,
            choices=[
                'aws',
                'azure',
                'gcp',
                'metal',
                'openstack',
                'vmware',
            ],
            help='target platform for install'
        )
        parser.add_argument(
            '--catalogs',
            action='append',
            choices=[
                'redhat-operators',
                'certified-operators',
                'redhat-marketplace',
                'community-operators',
            ],
            help='the catalog(s) content to download',
        )
        parser.add_argument(
            '--bundle-dir',
            help='directory to save downloaded content'
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='skip downloading content that already exists on disk'
        )
        parser.add_argument(
            '--skip-release',
            action='store_true',
            help='skip downloading of release content',
        )
        parser.add_argument(
            '--skip-catalogs',
            action='store_true',
            help='skip downloading of catalog content',
        )
        parser.add_argument(
            '--skip-rhcos',
            action='store_true',
            help='skip downloading of RHCOS image',
        )

    def parse_known_args(self):
        """
        Parse known args and also include extra args.
        """
        logger.debug('Parsing CLI arguments')

        known_args, extra_args = self.parser.parse_known_args()

        logger.debug('Known CLI arguments: %s', known_args)
        logger.debug('Extra CLI arguments: %s', extra_args)

        if not hasattr(known_args, 'action'):
            self.parser.print_help()
            sys.exit(1)
        return known_args, extra_args
