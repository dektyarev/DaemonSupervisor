# Daemon Supervisor

A tool which runs command as a child process in background and maintain running state.

## Getting Started

Make sure you have rwx permissions on your host to run daemon.

### Prerequisites

Python 2.6+ or 3.4+ version with python-dev libraries should be installed.

Following dependencies should be installed:
- python-daemon
- psutil

### Installation

Assuming required version Python is installed and running on your machine, 
make sure that python-dev libraries installed, if not use following command for CentOS/RHEL (for Python 3)
```
yum install gcc python3-devel
```

To install required packages:
```
pip3 install psutil python-daemon
```

Copy supervisor<nolink>.py and cmdargs<nolink>.py to your unix host.
Make sure supervisor<nolink>.py is executable:
```
chmod +x supervisor.py
```

## Usage

supervisor<nolink>.py [-h] [-f PID_FILE] [-l LOG_FILE] [-i CHECK_INTERVAL]
              [-n NUM_ATTEMPTS] [-s SECONDS_BETWEEN_RESTARTS]
              COMMAND

### Arguments

- -h    Prints help
- -w <WORK_DIR>, --work-dir=<WORK_DIR>  A work directory for daemon process. Default is '/var/lib/supervisor_daemon'.
- -f <PID_FILE>, --pid-file=<PID_FILE>  A pid file to be used as context of running daemon process. Default is '/var/run/supervisor_daemon.pid'.
- -l <LOG_FILE>, --log-file=<LOG_FILE>  Log file location. Default is '/var/log/supervisor_daemon.log'.
- -i <CHECK_INTERVAL>, --check-interval=<CHECK_INTERVAL>  An interval between process status checks, in seconds. Default is 1.
- -n <NUM_ATTEMPTS>, --num-attempts A number of attempts before giving up. Default is 3.
- -s <SECONDS_BETWEEN_RESTARTS>, --seconds-between-restarts=<SECONDS_BETWEEN_RESTARTS> Timeout between restart attempts in seconds. Default is 3.
- __COMMAND (Required)__ A command to run and supervise

### Examples

```
supervisor.py "bash -c \"sleep 10 && exit 0\""
```