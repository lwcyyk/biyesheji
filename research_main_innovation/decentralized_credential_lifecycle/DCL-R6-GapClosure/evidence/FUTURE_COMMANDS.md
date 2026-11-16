# BF-static-2/r4 下一执行命令字面表

本表仅供下一次授权审阅，执行次数0；权威argv来自execution_lock.json。禁止独立启动payload或worker；入口只通过冻结launcher。

## preparation_commands

~~~json
[
  [
    "/usr/bin/install",
    "-d",
    "-m",
    "0750",
    "-o",
    "root",
    "-g",
    "dcl-r6",
    "/var/lib/dcl-r6/batch04",
    "/var/lib/dcl-r6/batch04/inputs",
    "/var/lib/dcl-r6/batch04/reports"
  ],
  [
    "/usr/bin/install",
    "-d",
    "-m",
    "0700",
    "-o",
    "dcl-r6",
    "-g",
    "dcl-r6",
    "/var/lib/dcl-r6/batch04/out"
  ],
  [
    "/usr/bin/install",
    "-m",
    "0644",
    "-o",
    "root",
    "-g",
    "root",
    "/var/lib/dcl-r6/gc01/inputs/dclr6batch04.slice",
    "/etc/systemd/system/dclr6batch04.slice"
  ],
  [
    "/usr/bin/systemd-analyze",
    "verify",
    "/etc/systemd/system/dclr6batch04.slice"
  ],
  [
    "/usr/bin/systemctl",
    "daemon-reload"
  ]
]
~~~

## launch_command

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/guard.py",
  "--role",
  "launcher",
  "--batch-root",
  "/var/lib/dcl-r6/batch04"
]
~~~

## expected_C09_resume_command

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/guard.py",
  "--role",
  "launcher",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--resume"
]
~~~

## calibrate_only_launch_command

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/guard.py",
  "--role",
  "launcher",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--calibrate-only"
]
~~~

## calibrate_only_C09_resume_command

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/guard.py",
  "--role",
  "launcher",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--resume",
  "--calibrate-only"
]
~~~

## external_stop_command

~~~json
[
  "/usr/bin/systemd-run",
  "--no-block",
  "--unit=dclr6batch04-stop.service",
  "--property=Type=exec",
  "--property=Restart=no",
  "--property=User=root",
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/guard.py",
  "--role",
  "external-stop",
  "--batch-root",
  "/var/lib/dcl-r6/batch04"
]
~~~

## payload_commands / C00

~~~json
[
  "/usr/bin/systemd-run",
  "--no-block",
  "--unit=dclr6batch04-c00.service",
  "--property=User=dcl-r6",
  "--property=Group=dcl-r6",
  "--property=Type=exec",
  "--property=Slice=dclr6batch04.slice",
  "--property=LimitAS=1073741824:1073741824",
  "--property=TasksMax=4",
  "--property=TasksAccounting=yes",
  "--property=MemoryAccounting=yes",
  "--property=MemoryMax=4294967296",
  "--property=MemorySwapMax=0",
  "--property=OOMPolicy=kill",
  "--property=OOMScoreAdjust=0",
  "--property=LimitCORE=0",
  "--property=Restart=no",
  "--property=Delegate=no",
  "--property=NoNewPrivileges=yes",
  "--property=KillMode=control-group",
  "--property=KillSignal=SIGKILL",
  "--property=SendSIGKILL=yes",
  "--property=TimeoutStartSec=15",
  "--property=TimeoutStopSec=5",
  "--property=RuntimeMaxSec=1740",
  "--property=CapabilityBoundingSet=",
  "--property=AmbientCapabilities=",
  "--property=ProtectSystem=strict",
  "--property=ProtectHome=yes",
  "--property=ProtectControlGroups=yes",
  "--property=PrivateDevices=yes",
  "--property=PrivateTmp=yes",
  "--property=PrivateNetwork=yes",
  "--property=RestrictNamespaces=yes",
  "--property=RestrictAddressFamilies=AF_UNIX",
  "--property=ReadWritePaths=/var/lib/dcl-r6/batch04/out",
  "--property=WorkingDirectory=/var/lib/dcl-r6/batch04",
  "--property=UnsetEnvironment=LD_PRELOAD LD_LIBRARY_PATH LD_AUDIT PYTHONPATH PYTHONHOME",
  "--property=InaccessiblePaths=/mnt /init /dev/hugepages /usr/lib/wsl /run/systemd/private /run/dbus /run/user",
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/guard.py",
  "--role",
  "controller",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case",
  "C00"
]
~~~

## payload_commands / C01

~~~json
[
  "/usr/bin/systemd-run",
  "--no-block",
  "--unit=dclr6batch04-c01.service",
  "--property=User=dcl-r6",
  "--property=Group=dcl-r6",
  "--property=Type=exec",
  "--property=Slice=dclr6batch04.slice",
  "--property=LimitAS=1073741824:1073741824",
  "--property=TasksMax=4",
  "--property=TasksAccounting=yes",
  "--property=MemoryAccounting=yes",
  "--property=MemoryMax=4294967296",
  "--property=MemorySwapMax=0",
  "--property=OOMPolicy=kill",
  "--property=OOMScoreAdjust=0",
  "--property=LimitCORE=0",
  "--property=Restart=no",
  "--property=Delegate=no",
  "--property=NoNewPrivileges=yes",
  "--property=KillMode=control-group",
  "--property=KillSignal=SIGKILL",
  "--property=SendSIGKILL=yes",
  "--property=TimeoutStartSec=15",
  "--property=TimeoutStopSec=5",
  "--property=RuntimeMaxSec=1740",
  "--property=CapabilityBoundingSet=",
  "--property=AmbientCapabilities=",
  "--property=ProtectSystem=strict",
  "--property=ProtectHome=yes",
  "--property=ProtectControlGroups=yes",
  "--property=PrivateDevices=yes",
  "--property=PrivateTmp=yes",
  "--property=PrivateNetwork=yes",
  "--property=RestrictNamespaces=yes",
  "--property=RestrictAddressFamilies=AF_UNIX",
  "--property=ReadWritePaths=/var/lib/dcl-r6/batch04/out",
  "--property=WorkingDirectory=/var/lib/dcl-r6/batch04",
  "--property=UnsetEnvironment=LD_PRELOAD LD_LIBRARY_PATH LD_AUDIT PYTHONPATH PYTHONHOME",
  "--property=InaccessiblePaths=/mnt /init /dev/hugepages /usr/lib/wsl /run/systemd/private /run/dbus /run/user",
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/guard.py",
  "--role",
  "controller",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case",
  "C01"
]
~~~

## payload_commands / C02

~~~json
[
  "/usr/bin/systemd-run",
  "--no-block",
  "--unit=dclr6batch04-c02.service",
  "--property=User=dcl-r6",
  "--property=Group=dcl-r6",
  "--property=Type=exec",
  "--property=Slice=dclr6batch04.slice",
  "--property=LimitAS=1073741824:1073741824",
  "--property=TasksMax=4",
  "--property=TasksAccounting=yes",
  "--property=MemoryAccounting=yes",
  "--property=MemoryMax=4294967296",
  "--property=MemorySwapMax=0",
  "--property=OOMPolicy=kill",
  "--property=OOMScoreAdjust=0",
  "--property=LimitCORE=0",
  "--property=Restart=no",
  "--property=Delegate=no",
  "--property=NoNewPrivileges=yes",
  "--property=KillMode=control-group",
  "--property=KillSignal=SIGKILL",
  "--property=SendSIGKILL=yes",
  "--property=TimeoutStartSec=15",
  "--property=TimeoutStopSec=5",
  "--property=RuntimeMaxSec=1740",
  "--property=CapabilityBoundingSet=",
  "--property=AmbientCapabilities=",
  "--property=ProtectSystem=strict",
  "--property=ProtectHome=yes",
  "--property=ProtectControlGroups=yes",
  "--property=PrivateDevices=yes",
  "--property=PrivateTmp=yes",
  "--property=PrivateNetwork=yes",
  "--property=RestrictNamespaces=yes",
  "--property=RestrictAddressFamilies=AF_UNIX",
  "--property=ReadWritePaths=/var/lib/dcl-r6/batch04/out",
  "--property=WorkingDirectory=/var/lib/dcl-r6/batch04",
  "--property=UnsetEnvironment=LD_PRELOAD LD_LIBRARY_PATH LD_AUDIT PYTHONPATH PYTHONHOME",
  "--property=InaccessiblePaths=/mnt /init /dev/hugepages /usr/lib/wsl /run/systemd/private /run/dbus /run/user",
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/guard.py",
  "--role",
  "controller",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case",
  "C02"
]
~~~

## payload_commands / C03

~~~json
[
  "/usr/bin/systemd-run",
  "--no-block",
  "--unit=dclr6batch04-c03.service",
  "--property=User=dcl-r6",
  "--property=Group=dcl-r6",
  "--property=Type=exec",
  "--property=Slice=dclr6batch04.slice",
  "--property=LimitAS=1073741824:1073741824",
  "--property=TasksMax=4",
  "--property=TasksAccounting=yes",
  "--property=MemoryAccounting=yes",
  "--property=MemoryMax=4294967296",
  "--property=MemorySwapMax=0",
  "--property=OOMPolicy=kill",
  "--property=OOMScoreAdjust=0",
  "--property=LimitCORE=0",
  "--property=Restart=no",
  "--property=Delegate=no",
  "--property=NoNewPrivileges=yes",
  "--property=KillMode=control-group",
  "--property=KillSignal=SIGKILL",
  "--property=SendSIGKILL=yes",
  "--property=TimeoutStartSec=15",
  "--property=TimeoutStopSec=5",
  "--property=RuntimeMaxSec=1740",
  "--property=CapabilityBoundingSet=",
  "--property=AmbientCapabilities=",
  "--property=ProtectSystem=strict",
  "--property=ProtectHome=yes",
  "--property=ProtectControlGroups=yes",
  "--property=PrivateDevices=yes",
  "--property=PrivateTmp=yes",
  "--property=PrivateNetwork=yes",
  "--property=RestrictNamespaces=yes",
  "--property=RestrictAddressFamilies=AF_UNIX",
  "--property=ReadWritePaths=/var/lib/dcl-r6/batch04/out",
  "--property=WorkingDirectory=/var/lib/dcl-r6/batch04",
  "--property=UnsetEnvironment=LD_PRELOAD LD_LIBRARY_PATH LD_AUDIT PYTHONPATH PYTHONHOME",
  "--property=InaccessiblePaths=/mnt /init /dev/hugepages /usr/lib/wsl /run/systemd/private /run/dbus /run/user",
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/guard.py",
  "--role",
  "controller",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case",
  "C03"
]
~~~

## payload_commands / C04

~~~json
[
  "/usr/bin/systemd-run",
  "--no-block",
  "--unit=dclr6batch04-c04.service",
  "--property=User=dcl-r6",
  "--property=Group=dcl-r6",
  "--property=Type=exec",
  "--property=Slice=dclr6batch04.slice",
  "--property=LimitAS=1073741824:1073741824",
  "--property=TasksMax=4",
  "--property=TasksAccounting=yes",
  "--property=MemoryAccounting=yes",
  "--property=MemoryMax=4294967296",
  "--property=MemorySwapMax=0",
  "--property=OOMPolicy=kill",
  "--property=OOMScoreAdjust=0",
  "--property=LimitCORE=0",
  "--property=Restart=no",
  "--property=Delegate=no",
  "--property=NoNewPrivileges=yes",
  "--property=KillMode=control-group",
  "--property=KillSignal=SIGKILL",
  "--property=SendSIGKILL=yes",
  "--property=TimeoutStartSec=15",
  "--property=TimeoutStopSec=5",
  "--property=RuntimeMaxSec=1740",
  "--property=CapabilityBoundingSet=",
  "--property=AmbientCapabilities=",
  "--property=ProtectSystem=strict",
  "--property=ProtectHome=yes",
  "--property=ProtectControlGroups=yes",
  "--property=PrivateDevices=yes",
  "--property=PrivateTmp=yes",
  "--property=PrivateNetwork=yes",
  "--property=RestrictNamespaces=yes",
  "--property=RestrictAddressFamilies=AF_UNIX",
  "--property=ReadWritePaths=/var/lib/dcl-r6/batch04/out",
  "--property=WorkingDirectory=/var/lib/dcl-r6/batch04",
  "--property=UnsetEnvironment=LD_PRELOAD LD_LIBRARY_PATH LD_AUDIT PYTHONPATH PYTHONHOME",
  "--property=InaccessiblePaths=/mnt /init /dev/hugepages /usr/lib/wsl /run/systemd/private /run/dbus /run/user",
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/guard.py",
  "--role",
  "controller",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case",
  "C04"
]
~~~

## payload_commands / C05

~~~json
[
  "/usr/bin/systemd-run",
  "--no-block",
  "--unit=dclr6batch04-c05.service",
  "--property=User=dcl-r6",
  "--property=Group=dcl-r6",
  "--property=Type=exec",
  "--property=Slice=dclr6batch04.slice",
  "--property=LimitAS=1073741824:1073741824",
  "--property=TasksMax=4",
  "--property=TasksAccounting=yes",
  "--property=MemoryAccounting=yes",
  "--property=MemoryMax=4294967296",
  "--property=MemorySwapMax=0",
  "--property=OOMPolicy=kill",
  "--property=OOMScoreAdjust=0",
  "--property=LimitCORE=0",
  "--property=Restart=no",
  "--property=Delegate=no",
  "--property=NoNewPrivileges=yes",
  "--property=KillMode=control-group",
  "--property=KillSignal=SIGKILL",
  "--property=SendSIGKILL=yes",
  "--property=TimeoutStartSec=15",
  "--property=TimeoutStopSec=5",
  "--property=RuntimeMaxSec=1740",
  "--property=CapabilityBoundingSet=",
  "--property=AmbientCapabilities=",
  "--property=ProtectSystem=strict",
  "--property=ProtectHome=yes",
  "--property=ProtectControlGroups=yes",
  "--property=PrivateDevices=yes",
  "--property=PrivateTmp=yes",
  "--property=PrivateNetwork=yes",
  "--property=RestrictNamespaces=yes",
  "--property=RestrictAddressFamilies=AF_UNIX",
  "--property=ReadWritePaths=/var/lib/dcl-r6/batch04/out",
  "--property=WorkingDirectory=/var/lib/dcl-r6/batch04",
  "--property=UnsetEnvironment=LD_PRELOAD LD_LIBRARY_PATH LD_AUDIT PYTHONPATH PYTHONHOME",
  "--property=InaccessiblePaths=/mnt /init /dev/hugepages /usr/lib/wsl /run/systemd/private /run/dbus /run/user",
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/guard.py",
  "--role",
  "controller",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case",
  "C05"
]
~~~

## payload_commands / C06

~~~json
[
  "/usr/bin/systemd-run",
  "--no-block",
  "--unit=dclr6batch04-c06.service",
  "--property=User=dcl-r6",
  "--property=Group=dcl-r6",
  "--property=Type=exec",
  "--property=Slice=dclr6batch04.slice",
  "--property=LimitAS=1073741824:1073741824",
  "--property=TasksMax=4",
  "--property=TasksAccounting=yes",
  "--property=MemoryAccounting=yes",
  "--property=MemoryMax=4294967296",
  "--property=MemorySwapMax=0",
  "--property=OOMPolicy=kill",
  "--property=OOMScoreAdjust=0",
  "--property=LimitCORE=0",
  "--property=Restart=no",
  "--property=Delegate=no",
  "--property=NoNewPrivileges=yes",
  "--property=KillMode=control-group",
  "--property=KillSignal=SIGKILL",
  "--property=SendSIGKILL=yes",
  "--property=TimeoutStartSec=15",
  "--property=TimeoutStopSec=5",
  "--property=RuntimeMaxSec=1740",
  "--property=CapabilityBoundingSet=",
  "--property=AmbientCapabilities=",
  "--property=ProtectSystem=strict",
  "--property=ProtectHome=yes",
  "--property=ProtectControlGroups=yes",
  "--property=PrivateDevices=yes",
  "--property=PrivateTmp=yes",
  "--property=PrivateNetwork=yes",
  "--property=RestrictNamespaces=yes",
  "--property=RestrictAddressFamilies=AF_UNIX",
  "--property=ReadWritePaths=/var/lib/dcl-r6/batch04/out",
  "--property=WorkingDirectory=/var/lib/dcl-r6/batch04",
  "--property=UnsetEnvironment=LD_PRELOAD LD_LIBRARY_PATH LD_AUDIT PYTHONPATH PYTHONHOME",
  "--property=InaccessiblePaths=/mnt /init /dev/hugepages /usr/lib/wsl /run/systemd/private /run/dbus /run/user",
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/guard.py",
  "--role",
  "controller",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case",
  "C06"
]
~~~

## payload_commands / C07

~~~json
[
  "/usr/bin/systemd-run",
  "--no-block",
  "--unit=dclr6batch04-c07.service",
  "--property=User=dcl-r6",
  "--property=Group=dcl-r6",
  "--property=Type=exec",
  "--property=Slice=dclr6batch04.slice",
  "--property=LimitAS=1073741824:1073741824",
  "--property=TasksMax=4",
  "--property=TasksAccounting=yes",
  "--property=MemoryAccounting=yes",
  "--property=MemoryMax=4294967296",
  "--property=MemorySwapMax=0",
  "--property=OOMPolicy=kill",
  "--property=OOMScoreAdjust=0",
  "--property=LimitCORE=0",
  "--property=Restart=no",
  "--property=Delegate=no",
  "--property=NoNewPrivileges=yes",
  "--property=KillMode=control-group",
  "--property=KillSignal=SIGKILL",
  "--property=SendSIGKILL=yes",
  "--property=TimeoutStartSec=15",
  "--property=TimeoutStopSec=5",
  "--property=RuntimeMaxSec=1740",
  "--property=CapabilityBoundingSet=",
  "--property=AmbientCapabilities=",
  "--property=ProtectSystem=strict",
  "--property=ProtectHome=yes",
  "--property=ProtectControlGroups=yes",
  "--property=PrivateDevices=yes",
  "--property=PrivateTmp=yes",
  "--property=PrivateNetwork=yes",
  "--property=RestrictNamespaces=yes",
  "--property=RestrictAddressFamilies=AF_UNIX",
  "--property=ReadWritePaths=/var/lib/dcl-r6/batch04/out",
  "--property=WorkingDirectory=/var/lib/dcl-r6/batch04",
  "--property=UnsetEnvironment=LD_PRELOAD LD_LIBRARY_PATH LD_AUDIT PYTHONPATH PYTHONHOME",
  "--property=InaccessiblePaths=/mnt /init /dev/hugepages /usr/lib/wsl /run/systemd/private /run/dbus /run/user",
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/guard.py",
  "--role",
  "controller",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case",
  "C07"
]
~~~

## payload_commands / C08

~~~json
[
  "/usr/bin/systemd-run",
  "--no-block",
  "--unit=dclr6batch04-c08.service",
  "--property=User=dcl-r6",
  "--property=Group=dcl-r6",
  "--property=Type=exec",
  "--property=Slice=dclr6batch04.slice",
  "--property=LimitAS=1073741824:1073741824",
  "--property=TasksMax=4",
  "--property=TasksAccounting=yes",
  "--property=MemoryAccounting=yes",
  "--property=MemoryMax=4294967296",
  "--property=MemorySwapMax=0",
  "--property=OOMPolicy=kill",
  "--property=OOMScoreAdjust=0",
  "--property=LimitCORE=0",
  "--property=Restart=no",
  "--property=Delegate=no",
  "--property=NoNewPrivileges=yes",
  "--property=KillMode=control-group",
  "--property=KillSignal=SIGKILL",
  "--property=SendSIGKILL=yes",
  "--property=TimeoutStartSec=15",
  "--property=TimeoutStopSec=5",
  "--property=RuntimeMaxSec=1740",
  "--property=CapabilityBoundingSet=",
  "--property=AmbientCapabilities=",
  "--property=ProtectSystem=strict",
  "--property=ProtectHome=yes",
  "--property=ProtectControlGroups=yes",
  "--property=PrivateDevices=yes",
  "--property=PrivateTmp=yes",
  "--property=PrivateNetwork=yes",
  "--property=RestrictNamespaces=yes",
  "--property=RestrictAddressFamilies=AF_UNIX",
  "--property=ReadWritePaths=/var/lib/dcl-r6/batch04/out",
  "--property=WorkingDirectory=/var/lib/dcl-r6/batch04",
  "--property=UnsetEnvironment=LD_PRELOAD LD_LIBRARY_PATH LD_AUDIT PYTHONPATH PYTHONHOME",
  "--property=InaccessiblePaths=/mnt /init /dev/hugepages /usr/lib/wsl /run/systemd/private /run/dbus /run/user",
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/guard.py",
  "--role",
  "controller",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case",
  "C08"
]
~~~

## payload_commands / C09

~~~json
[
  "/usr/bin/systemd-run",
  "--no-block",
  "--unit=dclr6batch04-c09.service",
  "--property=User=dcl-r6",
  "--property=Group=dcl-r6",
  "--property=Type=exec",
  "--property=Slice=dclr6batch04.slice",
  "--property=LimitAS=1073741824:1073741824",
  "--property=TasksMax=4",
  "--property=TasksAccounting=yes",
  "--property=MemoryAccounting=yes",
  "--property=MemoryMax=4294967296",
  "--property=MemorySwapMax=0",
  "--property=OOMPolicy=kill",
  "--property=OOMScoreAdjust=0",
  "--property=LimitCORE=0",
  "--property=Restart=no",
  "--property=Delegate=no",
  "--property=NoNewPrivileges=yes",
  "--property=KillMode=control-group",
  "--property=KillSignal=SIGKILL",
  "--property=SendSIGKILL=yes",
  "--property=TimeoutStartSec=15",
  "--property=TimeoutStopSec=5",
  "--property=RuntimeMaxSec=1740",
  "--property=CapabilityBoundingSet=",
  "--property=AmbientCapabilities=",
  "--property=ProtectSystem=strict",
  "--property=ProtectHome=yes",
  "--property=ProtectControlGroups=yes",
  "--property=PrivateDevices=yes",
  "--property=PrivateTmp=yes",
  "--property=PrivateNetwork=yes",
  "--property=RestrictNamespaces=yes",
  "--property=RestrictAddressFamilies=AF_UNIX",
  "--property=ReadWritePaths=/var/lib/dcl-r6/batch04/out",
  "--property=WorkingDirectory=/var/lib/dcl-r6/batch04",
  "--property=UnsetEnvironment=LD_PRELOAD LD_LIBRARY_PATH LD_AUDIT PYTHONPATH PYTHONHOME",
  "--property=InaccessiblePaths=/mnt /init /dev/hugepages /usr/lib/wsl /run/systemd/private /run/dbus /run/user",
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/guard.py",
  "--role",
  "controller",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case",
  "C09"
]
~~~

## payload_commands / C10

~~~json
[
  "/usr/bin/systemd-run",
  "--no-block",
  "--unit=dclr6batch04-c10.service",
  "--property=User=dcl-r6",
  "--property=Group=dcl-r6",
  "--property=Type=exec",
  "--property=Slice=dclr6batch04.slice",
  "--property=LimitAS=1073741824:1073741824",
  "--property=TasksMax=4",
  "--property=TasksAccounting=yes",
  "--property=MemoryAccounting=yes",
  "--property=MemoryMax=4294967296",
  "--property=MemorySwapMax=0",
  "--property=OOMPolicy=kill",
  "--property=OOMScoreAdjust=0",
  "--property=LimitCORE=0",
  "--property=Restart=no",
  "--property=Delegate=no",
  "--property=NoNewPrivileges=yes",
  "--property=KillMode=control-group",
  "--property=KillSignal=SIGKILL",
  "--property=SendSIGKILL=yes",
  "--property=TimeoutStartSec=15",
  "--property=TimeoutStopSec=5",
  "--property=RuntimeMaxSec=1740",
  "--property=CapabilityBoundingSet=",
  "--property=AmbientCapabilities=",
  "--property=ProtectSystem=strict",
  "--property=ProtectHome=yes",
  "--property=ProtectControlGroups=yes",
  "--property=PrivateDevices=yes",
  "--property=PrivateTmp=yes",
  "--property=PrivateNetwork=yes",
  "--property=RestrictNamespaces=yes",
  "--property=RestrictAddressFamilies=AF_UNIX",
  "--property=ReadWritePaths=/var/lib/dcl-r6/batch04/out",
  "--property=WorkingDirectory=/var/lib/dcl-r6/batch04",
  "--property=UnsetEnvironment=LD_PRELOAD LD_LIBRARY_PATH LD_AUDIT PYTHONPATH PYTHONHOME",
  "--property=InaccessiblePaths=/mnt /init /dev/hugepages /usr/lib/wsl /run/systemd/private /run/dbus /run/user",
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/guard.py",
  "--role",
  "controller",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case",
  "C10"
]
~~~

## payload_commands / C11

~~~json
[
  "/usr/bin/systemd-run",
  "--no-block",
  "--unit=dclr6batch04-c11.service",
  "--property=User=dcl-r6",
  "--property=Group=dcl-r6",
  "--property=Type=exec",
  "--property=Slice=dclr6batch04.slice",
  "--property=LimitAS=1073741824:1073741824",
  "--property=TasksMax=4",
  "--property=TasksAccounting=yes",
  "--property=MemoryAccounting=yes",
  "--property=MemoryMax=4294967296",
  "--property=MemorySwapMax=0",
  "--property=OOMPolicy=kill",
  "--property=OOMScoreAdjust=0",
  "--property=LimitCORE=0",
  "--property=Restart=no",
  "--property=Delegate=no",
  "--property=NoNewPrivileges=yes",
  "--property=KillMode=control-group",
  "--property=KillSignal=SIGKILL",
  "--property=SendSIGKILL=yes",
  "--property=TimeoutStartSec=15",
  "--property=TimeoutStopSec=5",
  "--property=RuntimeMaxSec=1740",
  "--property=CapabilityBoundingSet=",
  "--property=AmbientCapabilities=",
  "--property=ProtectSystem=strict",
  "--property=ProtectHome=yes",
  "--property=ProtectControlGroups=yes",
  "--property=PrivateDevices=yes",
  "--property=PrivateTmp=yes",
  "--property=PrivateNetwork=yes",
  "--property=RestrictNamespaces=yes",
  "--property=RestrictAddressFamilies=AF_UNIX",
  "--property=ReadWritePaths=/var/lib/dcl-r6/batch04/out",
  "--property=WorkingDirectory=/var/lib/dcl-r6/batch04",
  "--property=UnsetEnvironment=LD_PRELOAD LD_LIBRARY_PATH LD_AUDIT PYTHONPATH PYTHONHOME",
  "--property=InaccessiblePaths=/mnt /init /dev/hugepages /usr/lib/wsl /run/systemd/private /run/dbus /run/user",
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/guard.py",
  "--role",
  "controller",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case",
  "C11"
]
~~~

## payload_commands / C12

~~~json
[
  "/usr/bin/systemd-run",
  "--no-block",
  "--unit=dclr6batch04-c12.service",
  "--property=User=dcl-r6",
  "--property=Group=dcl-r6",
  "--property=Type=exec",
  "--property=Slice=dclr6batch04.slice",
  "--property=LimitAS=1073741824:1073741824",
  "--property=TasksMax=4",
  "--property=TasksAccounting=yes",
  "--property=MemoryAccounting=yes",
  "--property=MemoryMax=4294967296",
  "--property=MemorySwapMax=0",
  "--property=OOMPolicy=kill",
  "--property=OOMScoreAdjust=0",
  "--property=LimitCORE=0",
  "--property=Restart=no",
  "--property=Delegate=no",
  "--property=NoNewPrivileges=yes",
  "--property=KillMode=control-group",
  "--property=KillSignal=SIGKILL",
  "--property=SendSIGKILL=yes",
  "--property=TimeoutStartSec=15",
  "--property=TimeoutStopSec=5",
  "--property=RuntimeMaxSec=1740",
  "--property=CapabilityBoundingSet=",
  "--property=AmbientCapabilities=",
  "--property=ProtectSystem=strict",
  "--property=ProtectHome=yes",
  "--property=ProtectControlGroups=yes",
  "--property=PrivateDevices=yes",
  "--property=PrivateTmp=yes",
  "--property=PrivateNetwork=yes",
  "--property=RestrictNamespaces=yes",
  "--property=RestrictAddressFamilies=AF_UNIX",
  "--property=ReadWritePaths=/var/lib/dcl-r6/batch04/out",
  "--property=WorkingDirectory=/var/lib/dcl-r6/batch04",
  "--property=UnsetEnvironment=LD_PRELOAD LD_LIBRARY_PATH LD_AUDIT PYTHONPATH PYTHONHOME",
  "--property=InaccessiblePaths=/mnt /init /dev/hugepages /usr/lib/wsl /run/systemd/private /run/dbus /run/user",
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/guard.py",
  "--role",
  "controller",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case",
  "C12"
]
~~~

## payload_commands / FORMAL

~~~json
[
  "/usr/bin/systemd-run",
  "--no-block",
  "--unit=dclr6batch04-formal.service",
  "--property=User=dcl-r6",
  "--property=Group=dcl-r6",
  "--property=Type=exec",
  "--property=Slice=dclr6batch04.slice",
  "--property=LimitAS=1073741824:1073741824",
  "--property=TasksMax=4",
  "--property=TasksAccounting=yes",
  "--property=MemoryAccounting=yes",
  "--property=MemoryMax=4294967296",
  "--property=MemorySwapMax=0",
  "--property=OOMPolicy=kill",
  "--property=OOMScoreAdjust=0",
  "--property=LimitCORE=0",
  "--property=Restart=no",
  "--property=Delegate=no",
  "--property=NoNewPrivileges=yes",
  "--property=KillMode=control-group",
  "--property=KillSignal=SIGKILL",
  "--property=SendSIGKILL=yes",
  "--property=TimeoutStartSec=15",
  "--property=TimeoutStopSec=5",
  "--property=RuntimeMaxSec=1740",
  "--property=CapabilityBoundingSet=",
  "--property=AmbientCapabilities=",
  "--property=ProtectSystem=strict",
  "--property=ProtectHome=yes",
  "--property=ProtectControlGroups=yes",
  "--property=PrivateDevices=yes",
  "--property=PrivateTmp=yes",
  "--property=PrivateNetwork=yes",
  "--property=RestrictNamespaces=yes",
  "--property=RestrictAddressFamilies=AF_UNIX",
  "--property=ReadWritePaths=/var/lib/dcl-r6/batch04/out",
  "--property=WorkingDirectory=/var/lib/dcl-r6/batch04",
  "--property=UnsetEnvironment=LD_PRELOAD LD_LIBRARY_PATH LD_AUDIT PYTHONPATH PYTHONHOME",
  "--property=InaccessiblePaths=/mnt /init /dev/hugepages /usr/lib/wsl /run/systemd/private /run/dbus /run/user",
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/guard.py",
  "--role",
  "controller",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case",
  "FORMAL"
]
~~~

## payload_commands / RANGE

~~~json
[
  "/usr/bin/systemd-run",
  "--no-block",
  "--unit=dclr6batch04-range.service",
  "--property=User=dcl-r6",
  "--property=Group=dcl-r6",
  "--property=Type=exec",
  "--property=Slice=dclr6batch04.slice",
  "--property=LimitAS=1073741824:1073741824",
  "--property=TasksMax=4",
  "--property=TasksAccounting=yes",
  "--property=MemoryAccounting=yes",
  "--property=MemoryMax=4294967296",
  "--property=MemorySwapMax=0",
  "--property=OOMPolicy=kill",
  "--property=OOMScoreAdjust=0",
  "--property=LimitCORE=0",
  "--property=Restart=no",
  "--property=Delegate=no",
  "--property=NoNewPrivileges=yes",
  "--property=KillMode=control-group",
  "--property=KillSignal=SIGKILL",
  "--property=SendSIGKILL=yes",
  "--property=TimeoutStartSec=15",
  "--property=TimeoutStopSec=5",
  "--property=RuntimeMaxSec=1740",
  "--property=CapabilityBoundingSet=",
  "--property=AmbientCapabilities=",
  "--property=ProtectSystem=strict",
  "--property=ProtectHome=yes",
  "--property=ProtectControlGroups=yes",
  "--property=PrivateDevices=yes",
  "--property=PrivateTmp=yes",
  "--property=PrivateNetwork=yes",
  "--property=RestrictNamespaces=yes",
  "--property=RestrictAddressFamilies=AF_UNIX",
  "--property=ReadWritePaths=/var/lib/dcl-r6/batch04/out",
  "--property=WorkingDirectory=/var/lib/dcl-r6/batch04",
  "--property=UnsetEnvironment=LD_PRELOAD LD_LIBRARY_PATH LD_AUDIT PYTHONPATH PYTHONHOME",
  "--property=InaccessiblePaths=/mnt /init /dev/hugepages /usr/lib/wsl /run/systemd/private /run/dbus /run/user",
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/guard.py",
  "--role",
  "controller",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case",
  "RANGE"
]
~~~

## safety_worker_commands / S1.before.safe

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S1.before.safe"
]
~~~

## safety_worker_commands / S1.before.mutant

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S1.before.mutant"
]
~~~

## safety_worker_commands / S2.unsynced.safe

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S2.unsynced.safe"
]
~~~

## safety_worker_commands / S2.unsynced.mutant

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S2.unsynced.mutant"
]
~~~

## safety_worker_commands / S2.confirmed.safe

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S2.confirmed.safe"
]
~~~

## safety_worker_commands / S2.confirmed.mutant

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S2.confirmed.mutant"
]
~~~

## safety_worker_commands / S2.unknown.safe

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S2.unknown.safe"
]
~~~

## safety_worker_commands / S2.unknown.mutant

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S2.unknown.mutant"
]
~~~

## safety_worker_commands / S3.committed.safe

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S3.committed.safe"
]
~~~

## safety_worker_commands / S3.committed.mutant

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S3.committed.mutant"
]
~~~

## safety_worker_commands / S4.claimed.safe

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S4.claimed.safe"
]
~~~

## safety_worker_commands / S4.claimed.mutant

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S4.claimed.mutant"
]
~~~

## safety_worker_commands / S5.same.safe

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S5.same.safe"
]
~~~

## safety_worker_commands / S5.same.mutant

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S5.same.mutant"
]
~~~

## safety_worker_commands / S5.conflict.safe

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S5.conflict.safe"
]
~~~

## safety_worker_commands / S5.conflict.mutant

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S5.conflict.mutant"
]
~~~

## safety_worker_commands / S6.concurrent.safe

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S6.concurrent.safe"
]
~~~

## safety_worker_commands / S6.concurrent.mutant

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S6.concurrent.mutant"
]
~~~

## safety_worker_commands / S7.short.safe

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S7.short.safe"
]
~~~

## safety_worker_commands / S7.short.mutant

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S7.short.mutant"
]
~~~

## safety_worker_commands / S7.fsync.safe

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S7.fsync.safe"
]
~~~

## safety_worker_commands / S7.fsync.mutant

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S7.fsync.mutant"
]
~~~

## safety_worker_commands / S8.closed.safe

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S8.closed.safe"
]
~~~

## safety_worker_commands / S8.closed.mutant

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S8.closed.mutant"
]
~~~

## safety_worker_commands / S8.expired.safe

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S8.expired.safe"
]
~~~

## safety_worker_commands / S8.expired.mutant

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S8.expired.mutant"
]
~~~

## safety_worker_commands / S8.boot.safe

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S8.boot.safe"
]
~~~

## safety_worker_commands / S8.boot.mutant

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S8.boot.mutant"
]
~~~

## safety_worker_commands / S8.lock.safe

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S8.lock.safe"
]
~~~

## safety_worker_commands / S8.lock.mutant

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S8.lock.mutant"
]
~~~

## safety_worker_commands / S8.restart.safe

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S8.restart.safe"
]
~~~

## safety_worker_commands / S8.restart.mutant

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S8.restart.mutant"
]
~~~

## safety_worker_commands / S9.exhausted.safe

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S9.exhausted.safe"
]
~~~

## safety_worker_commands / S9.exhausted.mutant

~~~json
[
  "/usr/bin/python3.12",
  "-I",
  "-S",
  "-B",
  "/var/lib/dcl-r6/gc01/src/range_fixtures.py",
  "--batch-root",
  "/var/lib/dcl-r6/batch04",
  "--case-id",
  "S9.exhausted.mutant"
]
~~~

## journal_export_command

只读导出本批16个服务当前boot的原始日志；当前执行0次。
~~~json
[
  "/usr/bin/journalctl",
  "--boot",
  "--no-pager",
  "--output=json",
  "--all",
  "--unit=dclr6batch04-c00.service",
  "--unit=dclr6batch04-c01.service",
  "--unit=dclr6batch04-c02.service",
  "--unit=dclr6batch04-c03.service",
  "--unit=dclr6batch04-c04.service",
  "--unit=dclr6batch04-c05.service",
  "--unit=dclr6batch04-c06.service",
  "--unit=dclr6batch04-c07.service",
  "--unit=dclr6batch04-c08.service",
  "--unit=dclr6batch04-c09.service",
  "--unit=dclr6batch04-c10.service",
  "--unit=dclr6batch04-c11.service",
  "--unit=dclr6batch04-c12.service",
  "--unit=dclr6batch04-formal.service",
  "--unit=dclr6batch04-range.service",
  "--unit=dclr6batch04-stop.service"
]
~~~