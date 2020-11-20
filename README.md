# OpenShift 4 Mirror

```bash
sudo yum install -y git python3 python3-pip
sudo pip3 install pipenv
```

```bash
git clone https://github.com/jaredhocutt/openshift4-mirror.git

cd openshift4-mirror
pipenv install
pipenv shell

./openshift_mirror bundle \
    --openshift-version 4.6.3 \
    --platform aws \
    --skip-existing \
    --pull-secret '{"auths":{"cloud.openshift.com":{"auth":"b3Blb...'
```
