#!/usr/bin/env python

import os
import sys
import shutil
import random
import shlex
import time
from stem import Signal
from stem.control import Controller
from subprocess import Popen


class Tor(object):
    initial_tor_port = 9060
    initial_tor_control_port = 9061
    tor_processes = 0

    def __init__(self):
        self.__class__.tor_processes = self.tor_processes + 1
        self.id = self.tor_processes
        self._create_torrc()
        self._create_data_directory()
        self.popen = Popen(['/usr/local/bin/tor', '-f', self.torrc()])

    def __del__(self):
        self._delete_torrc()
        self._delete_data_directory()
        self.popen.terminate()  # send signal
        self.popen.communicate()  # wait for process to die
        self.__class__.tor_processes = self.tor_processes - 1

    def port(self):
        return self.initial_tor_port + 2 * (self.tor_processes - 1)

    def control_port(self):
        return self.initial_tor_control_port + 2 * (self.tor_processes - 1)

    def renew_ip(self):
        self.log('Renewing IP')
        with Controller.from_port(port=self.control_port()) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)

    def log(self, str):
        print 'TOR#%i (Port:%i) %s' % (self.id, self.port(), str)

    def torrc(self):
        return '.torrc%i' % self.id

    def data_directory(self):
        return '.tor%i' % self.id

    def _create_torrc(self):
        if os.path.exists(self.torrc()):
            os.remove(self.torrc())
        f = open(self.torrc(), 'wb')
        f.write('SocksPort %i\n' % self.port() +
                'DataDirectory %s\n' % self.data_directory() +
                'ControlPort %i\n' % self.control_port() +
                'CookieAuthentication 0')
        f.close()

    def _delete_torrc(self):
        os.remove(self.torrc())

    def _create_data_directory(self):
        if os.path.exists(self.data_directory()):
            self._delete_data_directory()
        os.mkdir(self.data_directory())

    def _delete_data_directory(self):
        shutil.rmtree(self.data_directory())


class PhantomBot(object):
    command = "/usr/local/bin/phantomjs --proxy=127.0.0.1:%s --proxy-type=socks5 ./phantom.js"

    def __init__(self):
        self.tor = Tor()
        self.command_args = shlex.split(self.command % self.tor.port())
        self.max_votes_with_same_ip = None
        self.votes_with_same_ip = 0
        self._set_max_votes_with_same_ip()
        self.phantomjs = None

    def _set_max_votes_with_same_ip(self, min=1, max=10):
        self.max_votes_with_same_ip = random.randrange(min, max, 1)

    def _run_phantomjs(self):
        self.phantomjs = Popen(self.command_args, stdout=sys.stdout,
                               stderr=sys.stderr)

    def _has_phantomjs_terminated(self):
        return self.phantomjs.poll() is not None

    def vote(self):
        if self.phantomjs is None:
            self._vote()
        elif self._has_phantomjs_terminated():  # no voting in progress
            print self.phantomjs.stdout  # print phantomjs output
            self._vote()

    def _vote(self):
        # Renew IP if necessary
        if self.votes_with_same_ip == self.max_votes_with_same_ip:
            self.tor.renew_ip()
            self.votes_with_same_ip = 0
            self._set_max_votes_with_same_ip()  # change value each time to be more human

        self._run_phantomjs()
        self.votes_with_same_ip += 1


if __name__ == "__main__":

    num_bots = 1

    if len(sys.argv) > 1:
        num_bots = int(sys.argv[1])

    bots = [PhantomBot() for i in range(num_bots)]

    while True:
        for bot in bots:
            bot.vote()
            time.sleep(0.1)  # be gentle with CPU
