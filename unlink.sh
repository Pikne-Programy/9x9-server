#!/bin/sh
systemctl stop server9x9
rm /etc/systemd/system/server9x9.service
systemctl daemon-reload
