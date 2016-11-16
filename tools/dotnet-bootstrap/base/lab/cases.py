#!/usr/bin/env python 

# This shell script 'bakes' the docker containers that we depend on. Essentially, it sets up the docker containers in a certain manner where we
# are enabled to run a test case within them.

# to add a new platform to test on, simply create a directory (named anything that isn't already present) with a dockerfile in it. 

from shellcall import ShellCall
import sys

from sys import argv
from os import getcwd
import os
from os.path import join
from os.path import exists

# interface + data binding for managing the testcases.
class Cases:
    _supported_containers = join(getcwd(), 'containers/') # our 'list' of current supported platforms are the directories in this directory
    _testcases = join(getcwd(), 'cases/')

    # if current_working_directory = None, then we use the working dir dictated by the dockerfile
    # if none is specified in the dockerfile, then docker uses '/'
    def _docker_compose(self, identifier, local_volume, current_working_directory = None):
        wdir_parameter = None
        
        if current_working_directory:
            wdir_parameter = '-w "%s"'%(current_working_directory)
            
        return 'docker run %s -v %s:/env/dotnet-bootstrap dotnet-bootstrap:%s'%(wdir_parameter, local_volume, identifier)
    
    # Runs a select case
    def RunIn(self, container_name, casename):
        local_mount_location = join(self._supported_containers, container_name)
        testing_destination = join(local_mount_location, "testing/")
        
        ShellCall("echo \"running 'dotnet-bootstrap:%s - testcase: %s'\""%(container_name, casename))
        
        # copy the bootstrap and test source in to the container working directory (next to the Dockerfile)
        ShellCall('cp ../../dotnet.bootstrap.py %s'%(join(self._supported_containers, container_name)))
        ShellCall('mkdir -p %s'%(join(testing_destination, casename)))
        ShellCall('cp -R %s %s'%(join(self._testcases, casename), join(testing_destination, casename)))
        
        docker_run_cmd = 'docker run -v %s:/env/dotnet-bootstrap dotnet-bootstrap:%s'%(local_mount_location, str(container_name))
        # ^ : This runs docker using the current container directory (with the Dockerfile) as the current working directory.
        # so that anything placed in that directory becomes accessible. 
        # eventually we will copy the tests in to this directory as well (see below)
        
        # run the bootstrap
        ShellCall('%s python /env/dotnet-bootstrap/dotnet.bootstrap.py -to /env/dotnet-bootstrap/'%(docker_run_cmd)) # this will generate the src, obj, and bin directory here.
        
        # create whatever project file is the latest and greatest (was project.json, and is now named after the directory.csproj)
        ShellCall('%s /env/dotnet-bootstrap/bin/dotnet new -t Console'%(self._docker_compose(container_name, local_mount_location, join("/env/dotnet-bootstrap/testing/", casename))))
        
        ShellCall('cp -R %s/* %s'%(join(self._testcases, casename), join(testing_destination, casename)))
        
        # ShellCall('%s /env/dotnet-bootstrap/bin/dotnet restore .'%(self._docker_compose(container_name, local_mount_location, join("/env/dotnet-bootstrap/testing/", casename))))
        ShellCall('%s /env/dotnet-bootstrap/bin/dotnet run'%(self._docker_compose(container_name, local_mount_location, join("/env/dotnet-bootstrap/testing/", casename))))

    # runs the full matrix of tests
    def RunAll(self):
        for root, containers, files in os.walk(self._supported_containers):
            for container in containers: # we keep it explicitly the case that there are no other directories in the cases or containers directories.
                for root, cases, files in os.walk(self._testcases):
                    for case in cases:
                        self.RunIn(container, case) # runs the full matrix of environments and cases
                    
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
