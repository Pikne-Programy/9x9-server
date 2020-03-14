#!/bin/bash
check () {
  echo -n " "
  old_stty_cfg=$(stty -g)
  stty raw -echo
  answer=$( while ! head -c 1 | grep -i '[ny]' ;do true ;done )
  stty $old_stty_cfg
  if echo "$answer" | grep -iq "^y"; then
    echo Yes
    return 0
  else
    echo No
    return 1
  fi
}

systemwide="/usr/local/lib/9x9-server"
[[ $(id -u) = 0 ]] || { echo "no root, exitting..."; exit 1; }
cd "$(dirname "$0")"
if ! [ "`pwd`" = "$systemwide" ]; then
  echo "no system-wide"
  echo -n "Do you want to copy the whole current (`pwd`) folder to the system-wide location (y/n)?"
  check || { echo "no system-wide, exitting..."; exit 2; }

  if [[ -d "$systemwide" ]]; then
    echo -n "system-wide location exists; Do you want to remove system-wide version and replace it with that (y/n)?"
    check || { echo "no system-wide, exitting"; exit 3; }
    rm -r "$systemwide"
  fi
  [[ -f /etc/systemd/system/server9x9.service ]] && systemctl stop server9x9
  id server9x9 &>/dev/null && userdel server9x9
  useradd -r -s /bin/false server9x9
  mkdir "$systemwide"
  cp -r . "$systemwide"
  chown -R server9x9:server9x9 "$systemwide"
  echo "done"
  [[ -f /etc/sudoers.d/server9x9 ]] && rm /etc/sudoers.d/server9x9
  cat << EOT >> /etc/sudoers.d/server9x9
%server9x9 ALL= NOPASSWD: /bin/systemctl start server9x9
%server9x9 ALL= NOPASSWD: /bin/systemctl stop server9x9
%server9x9 ALL= NOPASSWD: /bin/systemctl status server9x9
EOT
  echo "falling to system-wide link.sh"
  cd "$systemwide"
  ./link.sh
  exit $?
fi
./unlink.sh
cp server9x9.service server9x9updater.service server9x9updater.timer  /etc/systemd/system/
systemctl daemon-reload
echo -n "Do you want to enable server9x9 (y/n)?"
check && systemctl enable server9x9
echo -n "Do you want to enable auto-updater (y/n)?"
check && systemctl enable server9x9updater.timer
echo -n "Do you want to start server9x9 (y/n)?"
check && { systemctl start server9x9; systemctl status server9x9; }
echo "DONE, exitting"
