#!/bin/bash

cd /tmp/
sudo rm -r *
git clone https://github.com/AGWA/git-crypt.git /tmp/git-crypt
cd /tmp/git-crypt
make
make install
