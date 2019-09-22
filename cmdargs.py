"""Command line arguments processor

This module contains funations to parse and check command line arguments
"""
import argparse

def check_string_not_empty(value: str):
    """Validates string is not empty
    
    Keyword arguments:
    value -- string to check

    Returns string if not empty
    """    
    if not value:
        raise argparse.ArgumentTypeError("empty string is not allowed")
    return value


def check_positive(value: str):
    """Validates that value is a positive integer
    
    Keyword arguments:
    value -- string containing integer value to check

    Returns positive integer value of argument
    """
    int_value = int(value)
    if int_value <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return int_value

def parse_arguments():
    """Parse and validates script parameters"""

    parser = argparse.ArgumentParser(description="This script launches Daemon Supervisor")
    parser.add_argument('-w', '--work-dir', type=check_string_not_empty,
                        default='/var/lib/supervisor_daemon', help='path to work directory')                        
    parser.add_argument('-f', '--pid-file', type=check_string_not_empty,
                        default='/var/run/supervisor_daemon.pid', help='path to pid file')
    parser.add_argument('-l', '--log-file', type=check_string_not_empty,
                        default='/var/log/supervisor_daemon.log', help='path to log file')
    parser.add_argument('-i', '--check-interval', type=check_positive,
                        default='1', help='check interval in seconds')
    parser.add_argument('-n', '--num-attempts', type=check_positive,
                        default='3', help='number of attempts before giving up')
    parser.add_argument('-s', '--seconds-between-restarts', type=check_positive,
                        default='3', help='timeout between restart attempts in seconds')
    parser.add_argument('command', type=check_string_not_empty,
                        help='a command to run and monitor')

    return parser.parse_args()