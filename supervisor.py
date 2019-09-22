#!/usr/bin/env python
import cmdargs
import logging
import time
import psutil
import subprocess
import shlex
import os
import sys
import daemon
import daemon.pidfile


DEFAULT_LOGGER_ID = "supervisor_daemon"
DEFAULT_UMASK = 0o002    # restrict all users to write/execture from this folder    


def init_logger(log_file: str):
    """Used to initialize logger for first use
    
    Keyword arguments:
    log_file -- log file location

    Returns initialized logger instace
    """
    logger = logging.getLogger(DEFAULT_LOGGER_ID)

    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(format_string)

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


def attempt_to_start_process(args: dict):
    """This function tries to run command several times based on args.num_attempts value
    
    Keyword arguments:
    args -- command line arguments dictionary

    Returns int with PID of started process on success, otherwise - None
    """
    logger = logging.getLogger(DEFAULT_LOGGER_ID)

    logger.info("Attempting to run command \"%s\"..." % args.command)

    for num_of_current_attempt in range(args.num_attempts):
        logger.info("Attempt #%s" % (num_of_current_attempt + 1))
        pid = start_process(args.command)

        # make sure process started successfully before returning pid
        if is_process_running(pid):
            logger.info("Started new process with PID: %s" % pid)
            return pid
        else:
            logger.error("Failed to run process")

        # wait for seconds_between_restarts interwal between attempts
        if num_of_current_attempt < args.num_attempts:
            time.sleep(float(args.seconds_between_restarts))

    logger.error("Process failed to start after %s attempt(s)." % args.num_attempts)
    return None


def start_process(command: str):
    """Used to run process based on command provided
    
    Keyword arguments:
    command -- command to run as new process  

    Returns PID of new process
    """
    logger = logging.getLogger(DEFAULT_LOGGER_ID)

    try:
        # tokenize command with lexer
        prepared_command = shlex.split(command)

        # start subprocess
        pid = subprocess.Popen(prepared_command).pid
    except FileNotFoundError as ex:
        logger.error("Invalid command \"%s\"" % command)
    except BaseException as ex:
        logger.exception(ex)
    else:
        return pid


def is_process_running(pid: int):
    """Checks if process with PID is running or waiting
    
    Keyword arguments:
    pid -- unix process identifier to check

    Returns True if process is running, otherwise false
    """
    if not pid:
        return False

    logger = logging.getLogger(DEFAULT_LOGGER_ID)

    try:
        process = psutil.Process(pid)
        logger.debug("Process %s status %s" % (pid, process.status()))
    except psutil.NoSuchProcess:
        logger.error("Process %s was not found" % pid)
    else:                
        # assume process in sleep state is running
        return process and process.status() in [psutil.STATUS_RUNNING, psutil.STATUS_SLEEPING]


def watch_process(args: dict):
    """Daemon entry point
    
    Keyword arguments:
    args -- command line arguments dictionary
    """
    logger = init_logger(args.log_file)

    supervisor_is_active = True
    pid = None      # pid of current process to monitor

    # loop for periodical checks of running process with check_interval
    while supervisor_is_active:
        logger.info("Checking status of process PID: %s running %s" %
                    (pid, is_process_running(pid)))

        # attempt to restart process if it is not running
        if not is_process_running(pid):
            pid = attempt_to_start_process(args)

        # wait for check_interval if process running, otherwise
        # consider process failed to restart after num_attempts
        if is_process_running(pid):
            time.sleep(float(args.check_interval))
        else:
            supervisor_is_active = False
            logger.info("Daemon Supervisor stopped")


def create_work_dir(path: str, umask: int):
    """Creates working directory if not available

    Keyword arguments:
    path -- path to create,
    umask -- access rights to set

    Returns True if directory available
    """
    if os.path.isdir(path) and os.access(path, umask):
        return True

    try:
        os.mkdir(path, umask)
    except OSError:
        print("Unable to create folder \"%s\"" % path)
        return False   

    return True


def get_context_pid(pid_filepath: str):
    """Retrieves PID of running daemon (if available)

    Keyword arguments:
    args -- command line arguments dictionary

    Returns PID of daemon context if present, otherwise None
    """
    if os.path.isfile(pid_filepath):        
        pid_file = open(pid_filepath, 'r')
        pid_str = pid_file.read()
        pid_file.close
        return pid_str
    return None

def start_daemon(args: dict):
    """Launches the daemon in its context
    
    Keyword arguments:
    args -- command line arguments dictionary
    """
    print("Starting Daemon Supervisor")    

    # check if context isn't available
    pid = get_context_pid(args.pid_file)
    if pid:        
        print("Daemon already running in this context with PID:%s" % pid)        
        return False

    # make sure working directory is available for use
    if not create_work_dir(args.work_dir, DEFAULT_UMASK):
        print("Unable to obtain work directory: %s" % args.work_dir)    
        return False    

    # initialize daemon context and run watcher process
    with daemon.DaemonContext(        
        working_directory=args.work_dir,        
        umask=DEFAULT_UMASK,
        pidfile=daemon.pidfile.PIDLockFile(args.pid_file),
    ) as _:        # context variable not used here
        watch_process(args)    


if __name__ == "__main__":
    """Launches Daemon Supervisor - 
    a tool to automatically run & monitor background process
    """

    # non-zero return code if daemon failed to launch
    if start_daemon(cmdargs.parse_arguments()):
        sys.exit(1)     
