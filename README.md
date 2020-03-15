# 9x9-server
The Server Software of 9x9 Game

## Installation

```
$ git clone https://github.com/Pikne-Programy/9x9-server.git
Cloning into '9x9-server'...
remote: Enumerating objects: 49, done.
remote: Counting objects: 100% (49/49), done.
remote: Compressing objects: 100% (29/29), done.
remote: Total 49 (delta 20), reused 48 (delta 19), pack-reused 0
Unpacking objects: 100% (49/49), done.
$ cd 9x9-server/
$ sudo ./link.sh 
no system-wide
Do you want to copy the whole current (~/9x9-server) folder to the system-wide location (y/n)? Yes
done
falling to system-wide link.sh
Do you want to enable server9x9 (y/n)? Yes
Created symlink /etc/systemd/system/multi-user.target.wants/server9x9.service → /etc/systemd/system/server9x9.service.
Do you want to enable and start auto-updater (y/n)? Yes
Created symlink /etc/systemd/system/timers.target.wants/server9x9updater.timer → /etc/systemd/system/server9x9updater.timer.
Do you want to start server9x9 (y/n)? Yes
● server9x9.service - 9x9 Server Service
   Loaded: loaded (/etc/systemd/system/server9x9.service; enabled; vendor preset: enabled)
   Active: active (running) since Sun 2020-03-15 17:13:05 CET; 22ms ago
 Main PID: 21770 (python3)
    Tasks: 1 (limit: 4659)
   Memory: 1.3M
   CGroup: /system.slice/server9x9.service
           └─21770 python3 /usr/local/lib/9x9-server/server.py

mar 15 17:13:05 administrator-virtual-machine systemd[1]: Started 9x9 Server Service.
DONE, exitting
$ cd ..
$ rm 9x9-server/ -rf
```
