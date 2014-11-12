set -e

NAME=$(python setup.py --name)
VERSION=$(python setup.py --version)

echo "Creating new version: ${NAME} ${VERSION}"

tox
git tag ${VERSION} -am "Version ${VERSION}"
python3 setup.py sdist bdist_egg bdist_wheel upload -r pypi
python2 setup.py bdist_wheel upload -r pypi
