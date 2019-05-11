#!/bin/bash

setup_aws(){
echo "Setting up AWS Credentials"
mkdir -p ~/.aws
cat > ~/.aws/credentials << EOL
[default]
aws_access_key_id = ${AWS_ACCESS_KEY_ID}
aws_secret_access_key = ${AWS_SECRET_ACCESS_KEY}
EOL

cat > ~/.aws/config << EOL
[default]
region = ${AWS_DEFAULT_REGION}
output = json
EOL
}

echo "On branch: $TRAVIS_BRANCH";

if [ "$TRAVIS_BRANCH" = "develop" ]
then
    setup_aws;
    echo "Updating api-dev...";
    zappa update dev;
elif [ "$TRAVIS_BRANCH" = "master" ]
then
    setup_aws;
    echo "Updating apiv1";
    zappa update prod;
else
    echo "Not on develop or master. No deployment.";
fi