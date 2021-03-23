#!/usr/bin/bash
source ~/.venv38/bin/activate

bigfile () {
    dvc add bigfile > /dev/null
    time dvc push bigfile > /dev/null
    time dvc status -c > /dev/null

    rm -rf bigfile .dvc/cache
    time dvc status -c > /dev/null
    time dvc pull bigfile > /dev/null

    rm -rf bigfile* .dvc/cache    
}

set -xe
rm -rf /tmp/test_dvc
mkdir /tmp/test_dvc
pushd /tmp/test_dvc
git init > /dev/null
dvc init > /dev/null

dvc remote add -d default s3://dvc-temp/s3fs-migration/h4-s3fs/

dd if=/dev/urandom of=bigfile bs=800000 count=600

time dvc gc -a -c -f > /dev/null

python ~/tooling/create_dataset.py dataset1 10000
dvc add dataset1 > /dev/null
time dvc push dataset1 > /dev/null
time dvc status -c > /dev/null
rm -rf dataset/1*

time dvc status -c > /dev/null


rm -rf dataset1 .dvc/cache
time dvc status -c > /dev/null
time dvc pull dataset1 > /dev/null

popd
