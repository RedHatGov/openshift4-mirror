# OpenShift 4 Mirror

## Run this app as a container in Podman

From an internet connected host, with Podman installed (tested on v2.1.1):
```bash
podman run -it -v ./:/app/bundle:Z quay.io/redhatgov/openshift4_mirror:latest
```
*Note: if no `--skip*` flags are provided, the download can be over 120Gb
Obtain your OpenShift pull secret from [Red Hat OpenShift Cluster Manager](cloud.redhat.com/openshift), you'll need to provide them to the `openshift_mirror` command below.


Run this from within the `openshift4_mirror` container:
* Note, refer to options flags below to determine what images you'd like to mirror
```bash
./openshift_mirror bundle \
    --openshift-version 4.6.3 \
    --platform aws \
    --skip-existing \
    --pull-secret '{"auths":{"cloud.openshift.com":{"auth":"b3Blb...'
```

Implemented providers for the `--platform`  flag are:
* aws
* azure
* vmware
* openstack
* metal
* gcp

After the download is finished:
```bash
exit
```

The result of this will be a local folder named by the OpenShift release, (4.6.3 in this example). It contains all files needed to move into a disconnected environment for an OpenShift 4.x deployment. Note, your Red Hat OpenShift `pull-secret.json` is also in this folder. Below is a tree output of a mirror operation that skips the catalog:
```
4.6.3/
├── bin
│   ├── kubectl
│   ├── oc
│   └── openshift-install
├── catalogs
├── clients
│   ├── openshift-client-linux.tar.gz
│   ├── openshift-install-linux.tar.gz
│   └── sha256sum.txt
├── pull-secret.json
├── release
│   ├── config
│   │   └── signature-sha256-14986d2b9c112ca9.yaml
│   └── v2
│       └── openshift
│           └── release
│               ├── blobs
│               │   ├── sha256:014ff151e98efa033f39aa6a68c816935bf00bf50a8437231f4c6cbc3ced208a
│               │   ├── sha256:0176ba5faf8ec9c316b38331848d27c9fe39fe491cc9facb97426ff8d8f226f9
|               │   ├── sha256:ff59396bcfee55afbfa3c761b7ba9cd4899d495081c002d829f959302471331b
│               │   └── sha256:fff7389977f8367b57b539f747979d274626a8f843fe4d9d9096e6fb531793fb
│               └── manifests
│                   ├── 4.6.3 -> sha256:14986d2b9c112ca955aaa03f7157beadda0bd3c089e5e1d56f28020d2dd55c52
│                   ├── 4.6.3-aws-ebs-csi-driver -> sha256:5e1c501e182b4c74a66c840991190c3179f831bbf5825d2837c7ca8d50dd61c9
│                   ├── 4.6.3-aws-ebs-csi-driver-operator -> sha256:f014470621514d00a3baf2a0cc72492b375e39925cf89475b6ee939b7d2bfd95
│                   └── sha256:fff7389977f8367b57b539f747979d274626a8f843fe4d9d9096e6fb531793fb
└── rhcos
    └── rhcos-aws.x86_64.vmdk.gz
```
For convenience, create a tarball from this directory:
```bash
tar -zcvf openshift-4-6-3.tar.gz 4.6.3
```

## openshift4_mirror help info

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