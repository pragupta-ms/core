#!/usr/bin/env python 

# This shell script 'bakes' the docker containers that we depend on. Essentially, it sets up the docker containers in a certain manner where we
# are enabled to run a test case within them.

# specify a single directory name to bake just a single container

from shellcall import ShellCall
import sys
import os

from sys import argv
from os.path import join
from os import getcwd

# interface + data binding for managing the containers.
class Containers:
    _supported_platforms = join(getcwd(), 'containers') + '/' # our 'list' of current supported platforms are the directories in this directory

    def Bake(self, selected_platform = None):
        ShellCall("echo baking 'cli-bootstrap:%s'"%(selected_platform))
        ShellCall("pushd %s"%(selected_platform))
        ShellCall("docker build -t \"cli-bootstrap:${%s}\" ."%(selected_platform))
        ShellCall("popd")

    def BakeAll(self):
        for root, platforms, files in os.walk(self._supported_platforms):
            for platform in platforms: # we keep it explicitly the case that there are no other directories in the cases or containers directories.
                Bake(platform)

    def List(self):
        ShellCall('ls -1 %s'%(self._supported_platforms))


def PrintUsage():
    print("TODO: Usage")

if __name__ == '__main__':
    containers = Containers()

    dictionary = { 
        "bake": containers.Bake,
        "list": containers.List
    }

    if len(argv) <= 1:
        PrintUsage()
        exit()

    dictionary[argv[1]]()
    
