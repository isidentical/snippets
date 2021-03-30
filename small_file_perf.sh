#!/usr/bin/bash
source ~/.venv38/bin/activate

set -xe
ulimit -Sn $(python -c "print(2**16)")
rm -rf /tmp/test_dvc
mkdir /tmp/test_dvc
pushd /tmp/test_dvc
git init > /dev/null
dvc init > /dev/null

dvc remote add -d default <fill>

python ~/tooling/create_dataset.py dataset1 10
dvc add dataset1 > /dev/null
time dvc push dataset1
rm -rf dataset1 .dvc/cache
time dvc pull dataset1 > /dev/null

popd
