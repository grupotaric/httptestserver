set -e

NAME=$(python setup.py --name)
VERSION=$(python setup.py --version)

echo "Creating new version: ${NAME} ${VERSION}"

tox
git tag ${VERSION} -am "Version ${VERSION}"

echo "Uploading python3 version to pypi"
virtualenv env3 --python /usr/bin/python3
env3/bin/pip install wheel
env3/bin/python setup.py sdist bdist_wheel upload -r pypi

echo "Uploading python2 version to pypi"
virtualenv env2 --python /usr/bin/python2
env2/bin/pip install wheel
env2/bin/python setup.py bdist_wheel upload -r pypi
