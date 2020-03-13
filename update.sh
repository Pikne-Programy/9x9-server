#!/bin/bash
git fetch
[[ $(git rev-parse HEAD) == $(git rev-parse @{u}) ]] && { echo "Already up to date, exitting..."; exit 0; }
sudo systemctl stop server9x9
sudo systemctl status server9x9
git pull
sudo systemctl start server9x9
sudo systemctl status server9x9
