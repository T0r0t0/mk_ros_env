#!/usr/bin/env python3

import argparse
import os
from docker_generator import docker_generator

parser = argparse.ArgumentParser(description="This script generate an isolate environment for your ros application. It use container with Docker framework.")
parser.add_argument("-n", "--name", help="This will be the name of the container. By default is ros-<distro>", required=False)
parser.add_argument("--ros-version",help="Version of ROS. Can be ROS2: humble, galactic, jazzy,... or even ROS1: noetic, melodic, ...\n If not specify the default distros humble", required=False)
parser.add_argument("-g", "--gazebo", help="Add all dependencies for using gzebo in the corresponding version", action="store_true", required=False)
parser.add_argument("-p", "--path", help="Specify a folder to copy with the ros environment. Most of the time is an existing source folder. If not defined an empty folder named 'ros_ws' will be create.", required=False)
parser.add_argument("-s", "--shared", help="Share the folder created or specify by --path to the container", action="store_true")
parser.add_argument("-e", "--env", help="You can specify a list of environment variables from a .txt file. They will be added to the default environment variable.", required=False)
parser.add_argument("-d", "--dependencies", help="You probably need specific dependencies for your project. Add them with a list in a .txt file.", required=False)

if __name__=="__main__":
    args = parser.parse_args()
    print(f"You have chosen ROS {args.ros_version} with the following option: ")
    print(f"\nContainer name: {args.name}")
    print(f'\tGazebo : {args.gazebo}')
    if args.shared: print(f'\tshared folder : {args.path}')
    else: print(f'\tcopy folder : {args.path}')
    print(f'\tenvironment variables : {args.env}')
    print(f'\tDependencies : {args.dependencies}')


    docker_generator(args.name, args.gazebo, args.path, args.shared, args.env, args.dependencies, args.ros_version)
    

