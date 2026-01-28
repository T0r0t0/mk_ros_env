#!/usr/bin/env python3

import subprocess
import argparse
import os
import sys
from docker_generator import docker_generator
from docker_tools import docker_tools

name = "ros-humble"

parser = argparse.ArgumentParser(description="This script generate an isolate environment for your ros application. It use container with Docker framework.")

command_subparser = parser.add_subparsers(dest="command", help="Available commands", required=True)
create_parser = command_subparser.add_parser("create", help="Create necessary file for ros environment in docker")

create_parser.add_argument("-n", "--name", help="This will be the name of the container. By default is ros-<distro>", required=False)
create_parser.add_argument("--ros-version",help="Version of ROS. Can be ROS2: humble, galactic, jazzy,... or even ROS1: noetic, melodic, ...\n If not specify the default distros humble", required=False)
create_parser.add_argument("-g", "--gazebo", help="Add all dependencies for using gzebo in the corresponding version", action="store_true", required=False)
create_parser.add_argument("-p", "--path", help="Specify a folder to copy with the ros environment. Most of the time is an existing source folder. If not defined an empty folder named 'ros_ws' will be create.", required=False)
create_parser.add_argument("-s", "--shared", help="Share the folder created or specify by --path to the container", action="store_true")
create_parser.add_argument("-e", "--env", help="You can specify a list of environment variables from a .txt file. They will be added to the default environment variable.", required=False)
create_parser.add_argument("-d", "--dependencies", help="You probably need specific dependencies for your project. Add them with a list in a .txt file.", required=False)

create_parser = command_subparser.add_parser("delete", help="Delete created file for ros environment in docker. Dockerfile, docker-compose.yaml, .env. And rm all docker contianers and images.")
create_parser = command_subparser.add_parser("build", help="Build the image. WARN: Need to be execute after the create commands")
create_parser = command_subparser.add_parser("start", help="Start the containers. From the corresponding image")
create_parser = command_subparser.add_parser("stop", help="Stop the containers.")
create_parser = command_subparser.add_parser("kill", help="Kill the containers wihtout removing the image.")


if __name__=="__main__":

    # Print the help if no command are given
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Analyser les arguments
    args = parser.parse_args()

    if args.command == "create":
        print(f"You have chosen ROS {args.ros_version} with the following option: ")
        print(f"\nContainer name: {args.name}")
        print(f'\tGazebo : {args.gazebo}')
        if args.shared: print(f'\tshared folder : {args.path}')
        else: print(f'\tcopy folder : {args.path}')
        print(f'\tenvironment variables : {args.env}')
        print(f'\tDependencies : {args.dependencies}')
        docker_generator(args.name, args.gazebo, args.path, args.shared, args.env, args.dependencies, args.ros_version)

    elif args.command == "delete":
        print("Deleting files...")
        if os.path.exists("./Dockerfile"):
            os.remove("./Dockerfile")
            print("\tDockerfile deleted.")
        if os.path.exists("./docker-compose.yaml"):
            os.remove("./docker-compose.yaml")
            print("\t docker-compose.yaml deleted.")
        if os.path.exists("./.env"):
            os.remove("./.env")
            print("\t.env deleted.")


        print("Deleting docker container :")
        if docker_tools.isRunning(name):
            if docker_tools.stop(name) and docker_tools.rm(name):
                print("Isolate environment killed.")
        elif docker_tools.exist(name):
            if docker_tools.rm(name):
                print("Isolate environment killed.")

        print("Deleting images:")
        docker_tools.rmi(name)
        print("Delete completed !")

    elif args.command == "build":
        docker_tools.build()

    elif args.command == "start":
        # if never start: docker compose up -d else: docker start and open the bash terminal (without forgetting xhost +)

        if docker_tools.isRunning(name): # If is already running
            print("Already start ! ")

        elif docker_tools.exist(name):
            print("Already exist so start it")
            docker_tools.start(name)

        else: # Does not exist so we create it 
            print("Doesn't exist ! Creation ...")
            process = subprocess.Popen("docker compose up -d", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Read the output in real-time
            for line in process.stdout:
                print(line.strip())
            return_code = process.wait()

        #Connect the terminal stream to the docker
        print("Connection to isolate environment ...")
        docker_tools.attachTerminal(name)
        print("Exit of the isolate environment.\nHave a nice day ! ;)")

    elif args.command == "stop":
        name="my_dock"
        if docker_tools.isRunning(name): # If is already running
            docker_tools.stop(name)
        else:
            print("Already stopped or maybe doesn't exist.")

    elif args.command == "kill":
        # docker stop and docker rm

        if docker_tools.isRunning(name):
            if docker_tools.stop(name) and docker_tools.rm(name):
                print("Isolate environment killed.")
        elif docker_tools.exist(name):
            if docker_tools.rm(name):
                print("Isolate environment killed.")
        else:
            print("Isolate environment already killed or has never existed.")





