#!/bin/bash
[[ $(id -u) = 0 ]] || { echo "no root, exitting..."; exit 1; }
[[ -f /etc/systemd/system/server9x9updater.timer ]] && { systemctl stop server9x9updater.timer; systemctl disable server9x9updater.timer; rm /etc/systemd/system/server9x9updater.timer; }
[[ -f /etc/systemd/system/server9x9updater.service ]] && { systemctl stop server9x9updater.service; rm /etc/systemd/system/server9x9updater.service; }
[[ -f /etc/systemd/system/server9x9.service ]] && { systemctl stop server9x9; systemctl disable server9x9;  rm /etc/systemd/system/server9x9.service; }
systemctl daemon-reload
systemctl reset-failed
