#!/usr/bin/env python 

# This shell script 'bakes' the docker containers that we depend on. Essentially, it sets up the docker containers in a certain manner where we
# are enabled to run a test case within them.

# to add a new platform to test on, simply create a directory (named anything that isn't already present) with a dockerfile in it. 

from shellcall import ShellCall
import sys

from sys import argv
from os import getcwd
from os.path import join
from os.path import exists

# interface + data binding for managing the testcases.
class Cases:
    _supported_containers = join(getcwd(), 'containers') + '/' # our 'list' of current supported platforms are the directories in this directory
    _testcases = join(getcwd(), 'cases') + '/'

    # Runs a select case
    def RunIn(self, container_name = None, casename = None):
        ShellCall("echo \"running 'dotnet-bootstrap:%s'\""%(selected_case))
        ShellCall("pushd %s"%(join(_testcases, selected_case)))
        
        # copy the bootstrap in to place.
        ShellCall("cp ../../../dotnet.bootstrap.py .")

        # this will mount our current directory as the working directory in the docker containers, then we run the bootstrap to produce a src, obj, and bin directory.
        docker_run_cmd = 'docker run -v %s:/env/dotnet-bootstrap dotnet-bootstrap:%s'

        ShellCall('%s python dotnet.bootstrap.py -to .'%(docker_run_cmd, getcwd(), container_name)) # this will generate the src, obj, and bin directory here.
        ShellCall('%s ./bin/dotnet restore'%(docker_run_cmd))
        ShellCall('%s ./bin/dotnet run'%(docker_run_cmd))

        # copy test cases to this platform
        ShellCall('popd')

    # runs the full matrix of tests
    def RunAll(self):
        for root, containers, files in os.walk(self._supported_containers):
            for container in containers: # we keep it explicitly the case that there are no other directories in the cases or containers directories.
                for root, cases, files in os.walk(self._testcases):
                    for case in cases:
                        RunIn(container, case) # runs the full matrix of environments and cases
                    
                    break # just walk the top level
            break # just walk the top level.

    def List(self):
        ShellCall('ls -1 %s'%(self._testcases))

    def __init__(self):
        if not exists(self._supported_containers):
            print('no such directory: %s\n'%(self._supported_containers))
            sys.exit()

        if not exists(self._testcases):
            print('no such directory: %s\n'%(self._testcases))
            sys.exit()
            
def PrintUsage():
    print("TODO: Usage")

if __name__ == '__main__':
    testcases = Cases()

    if len(argv) <= 1:
        PrintUsage()
        exit()

    dictionary = { 
        "run": testcases.RunAll,
        "list": testcases.List
    }

    dictionary[argv[1]]()
