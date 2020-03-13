#!/bin/sh
systemctl stop server9x9
rm /etc/systemd/system/server9x9.service /etc/systemd/system/server9x9updater.service /etc/systemd/system/server9x9updater.timer
systemctl daemon-reload
