#!/usr/bin/env bash
rm -rf lambda_build
mkdir lambda_build
pushd lambda_build

virtualenv dist_env
source dist_env/bin/activate

pip install -r ../requirements.txt
deactivate

mkdir dist

cp -R dist_env/lib/python2.7/site-packages/* dist/
cp -R dist_env/lib64/python2.7/site-packages/* dist/
cp ../server_lambda.py dist/

cd dist

zip -r dist.zip *

# aws lambda update-function-code --function-name auto-order-lambda --zip-file fileb://dist.zip --region us-east-1

popd
