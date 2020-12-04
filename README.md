# OpenShift 4 Mirror

## Initial Setup

Install system dependencies.

```bash
sudo yum install -y git python3 python3-pip
sudo pip3 install pipenv
```

Clone the repository.

```bash
git clone https://github.com/jaredhocutt/openshift4-mirror.git
```

Install the Python dependencies.

```bash
cd openshift4-mirror
pipenv install
```

## Usage

Activate the virtual Python environment and run the bundle automation.

```bash
pipenv shell

./openshift_mirror bundle \
    --openshift-version 4.6.3 \
    --platform aws \
    --skip-existing \
    --pull-secret '{"auths":{"cloud.openshift.com":{"auth":"b3Blb...'
```

For additional options, check out the help pages.

```bash
./openshift_mirror -h
usage: openshift_mirror [-h] {bundle,build,shell} ...

Utility for mirroring OpenShift 4 content.

positional arguments:
  {bundle,build,shell}
    bundle              bundle the OpenShift content
    build               build the container image
    shell               open a shell in the container environment

optional arguments:
  -h, --help            show this help message and exit
```

At the moment, `build` and `shell` don't do anything, so what you really want
to check out is the help page for `bundle`.

```bash
./openshift_mirror bundle -h
usage: openshift_mirror bundle [-h] --openshift-version OPENSHIFT_VERSION --pull-secret PULL_SECRET --platform {aws,azure,gcp,metal,openstack,vmware}
                               [--catalogs {redhat-operators,certified-operators,redhat-marketplace,community-operators}] [--bundle-dir BUNDLE_DIR] [--skip-existing] [--skip-release] [--skip-catalogs]
                               [--skip-rhcos]

optional arguments:
  -h, --help            show this help message and exit
  --openshift-version OPENSHIFT_VERSION
                        the OpenShift version (e.g. 4.5.11)
  --pull-secret PULL_SECRET
                        the content of your pull secret (can be found at https://cloud.redhat.com/openshift/install/pull-secret)
  --platform {aws,azure,gcp,metal,openstack,vmware}
                        target platform for install
  --catalogs {redhat-operators,certified-operators,redhat-marketplace,community-operators}
                        the catalog(s) content to download
  --bundle-dir BUNDLE_DIR
                        directory to save downloaded content
  --skip-existing       skip downloading content that already exists on disk
  --skip-release        skip downloading of release content
  --skip-catalogs       skip downloading of catalog content
  --skip-rhcos          skip downloading of RHCOS image
```
