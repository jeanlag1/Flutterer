"""
File: run_server.py

NOTE TO STUDENTS: You don't need to read anything in this file.

Standalone application that (re)runs a given command
when related files change:

usage: run_server.py [-h] [-g GLOB [-g GLOB, ...]] [COMMAND]

optional positional arguments:
  COMMAND               The command to (re)run upon file changes

optional switch arguments:
  -h, --help            show this help message and exit
  -g GLOB, --glob GLOB  The glob(s) to search in order to add files.

Ignores files contained in directories with "__" in their name.
If no file globs are specified, defaults to DEFAULT_GLOB, defined below.
If no command is specified, defaults to DEFAULT_ARGV, defined below.

NOTE TO STUDENTS: You don't need to read anything in this file.
"""

import argparse
import asyncio
import glob
import os.path
import subprocess
import sys
import time
from collections import defaultdict
from typing import Set, Iterable, List, Callable, Coroutine

from server.colorama import Fore, Style, init

SERVER_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "server")
SERVE_PATH = os.path.join(SERVER_DIR, "serve.py")
DEFAULT_ARGV = [sys.executable, SERVE_PATH]  # Run our server :)
DEFAULT_GLOB = [os.path.join(SERVER_DIR, "**.py")]

DEFAULT_POLL_INTERVAL = 0.5  # second(s)
DEFAULT_TERMINATE_TIMEOUT = 5  # second(s)

# determines how often the application wakes up to check its child process.
PROCESS_STATE_CHECK_INTERVAL = 0.1  # second(s)
CTRL_C_RESTART_DELAY = 1  # second(s)


def get_args() -> argparse.Namespace:
    """
    Parses all command line arguments, and applies defaults if those options weren't specified.
    """

    parser = argparse.ArgumentParser(description="Automatically (re)runs the given script when files change.")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="The command to (re)run upon file changes",
                        metavar="COMMAND")
    parser.add_argument("-g", "--glob", dest="globs", action="append", metavar="GLOB")

    args = parser.parse_args()
    if args.globs is None:
        args.globs = DEFAULT_GLOB
    if args.command is None or args.command == []:
        args.command = DEFAULT_ARGV

    return args


def get_files(globs: Iterable[str]) -> Set[str]:
    """
    Given an iterable of globs, finds all files it matches (recursively),
    ignoring files within directories containing __
    """

    files = set()

    for g in globs:
        for path in glob.glob(g, recursive=True):
            # only adds files, and only if their path doesn't contain __ (e.g. __pycache__)
            if "__" not in os.path.dirname(path) and os.path.isfile(path):
                files.add(path)

    return files


def hotreload_print(*args, **kwargs):
    """
    Calls print, prefixing with a timestamp and "[Hot Reload]", and suffixed
    with a terminal style reset instruction.  All args and kwargs are forwarded
    to print.
    """
    timestamp = time.strftime("%I:%M:%S %p").lower()
    print(f"{Fore.LIGHTBLACK_EX}{timestamp}{Style.RESET_ALL} {Fore.LIGHTMAGENTA_EX}[Hot Reload]{Style.RESET_ALL}",
          *args, Style.RESET_ALL, **kwargs)


class FilePollMonitor:
    """
    Asynchronously polls a given list of globs at a given time interval. Upon
    noticing updated files, calls the given action.
    """

    def __init__(self, globs: List[str], action: Callable[[], any], interval=DEFAULT_POLL_INTERVAL):
        self._globs = globs
        self._action = action
        self._interval = interval
        self._running = False
        self._modtimes = defaultdict(float)
        self._started = False
        self.__files_modified()  # populates the initial _modtimes dictionary.

    def __files_modified(self) -> bool:
        """
        Iterates over all the given files, updating our record of their
        modification times. Returns true if a file has been modified since last
        time the method was run.
        """
        changed = False
        for file in get_files(self._globs):  # called every time to detect new files.
            try:
                mtime = os.path.getmtime(file)
                if self._modtimes[file] < mtime:
                    self._modtimes[file] = mtime
                    changed = True
            except OSError:  # file not found/file removed
                if file in self._modtimes:
                    del self._modtimes[file]
                    changed = True
        return changed

    async def __run(self):
        """
        Poll coroutine
        """
        try:
            while self._running:
                if self.__files_modified():
                    self._action()
                await asyncio.sleep(self._interval)
        except KeyboardInterrupt:
            pass  # ignore keyboard interrupts in this coroutine... handled outside.

    def start(self) -> Coroutine:
        """
        Initializes the poll coroutine and returns it.
        """
        self._running = True
        return self.__run()

    def stop(self):
        """
        Signals the poll coroutine to stop next time it runs.
        """
        self._running = False


class MonitoredProcess:
    """
    Defines a process that will be (re)started each time a file defined in the
    given list of globs is changed.

    If the process is running when files are changed, it will ask it to
    terminate using SIGTERM, wait 5 seconds, and send a SIGKILL after.
    Note that Windows does not make a differentiation between these.
    """

    def __init__(self, argv: List[str], globs: List[str]):
        self._argv = argv
        self._current = None
        self._monitor = FilePollMonitor(globs, self.__reexec_process)
        self._monitor_task = None
        self._has_exit = False
        self._started = False

    def __end_process(self):
        """
        Tries to gently terminate the process by sending SIGTERM, then waiting
        DEFAULT_TERMINATE_TIMEOUT seconds, then sending a SIGKILL.
        """
        self._current.terminate()
        try:
            self._current.wait(timeout=DEFAULT_TERMINATE_TIMEOUT)

        except subprocess.TimeoutExpired:
            self._current.kill()

    def __exec_process(self):
        """
        Creates a new instance of the process defined by self._argv, setting
        instance variables accordingly.
        """
        hotreload_print(f"{Fore.MAGENTA}Starting process...")
        proc = subprocess.Popen(self._argv, shell=False)
        self._current = proc
        self._has_exit = False

    def __reexec_process(self):
        """
        Restarts the process if it's running, or simply starts it if it's not
        running.
        """
        hotreload_print(f"{Fore.YELLOW}Change detected.")

        if self._current and self._current.poll() is None:
            hotreload_print(f"{Fore.YELLOW}Process is still running. Ending...")
            self.__end_process()

        self.__exec_process()

    def __notify_state_change(self):
        """
        Notices if the application has recently exited and notifies the user.
        """
        exit_code = self._current.poll()

        if not self._has_exit and exit_code is not None:
            self._has_exit = True
            if exit_code == 0:
                hotreload_print(f"{Fore.GREEN}The process exited with exit code 0.{Style.RESET_ALL}")
            else:
                hotreload_print(f"{Fore.RED}The process exited with exit code {exit_code}{Style.RESET_ALL}")

    async def __monitor(self):
        """
        The monitor coroutine.
        """
        try:
            self.__exec_process()

            self._monitor_task = asyncio.create_task(self._monitor.start())
            while self._started:
                self.__notify_state_change()
                await asyncio.sleep(PROCESS_STATE_CHECK_INTERVAL)
        except KeyboardInterrupt:
            pass  # ignore keyboard interrupts in this coroutine... handled outside.

    def start(self):
        """
        Blocking. Starts the hot reload process for this monitored process.
        """
        self._started = True
        asyncio.run(self.__monitor())

    def stop(self):
        """
        Stops all monitoring processes the next time it wakes up, and
        immediately stops the process, if it's running.
        """
        self._started = False
        self._monitor.stop()
        if self._current:
            self.__end_process()


def hotreload(argv: List[str], globs: List[str]):
    """
    Constructs a MonitoredProcess and starts it.  Handles ^C by
    force-restarting the process; if ^C is pressed twice in quick succession,
    quits out of the app.
    """
    mp = MonitoredProcess(argv, globs)
    while True:
        try:
            mp.start()
        except KeyboardInterrupt:
            timeout_words = f"{CTRL_C_RESTART_DELAY} second"
            if CTRL_C_RESTART_DELAY != 1:
                timeout_words += "s"

            hotreload_print(f"{Fore.CYAN}Force restarting... Press Ctrl+C again within {timeout_words} to quit")
            mp.stop()
            try:
                time.sleep(CTRL_C_RESTART_DELAY)
            except KeyboardInterrupt:
                hotreload_print(f"{Fore.CYAN}Done.")
                return


if __name__ == "__main__":
    init()  # colorama - initializes terminal color support.
    args = get_args()

    hotreload(args.command, args.globs)
