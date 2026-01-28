#!/usr/bin/env python3

import subprocess
import argparse
import os
import sys
import yaml
from docker_generator import docker_generator
from docker_tools import docker_tools
from RosEnvParam import RosEnvParam

parser = argparse.ArgumentParser(description="This script generate an isolate environment for your ros application. It use container with Docker framework.")
parser.add_argument("--param-path", help="path to a RosEnvParam.yaml file. By default: ./.RosEnvParam.yaml", default=".ros_env_param.yaml", required=False)

command_subparser = parser.add_subparsers(dest="command", help="Available commands", required=True)
create_parser = command_subparser.add_parser("create", help="Create necessary file for ros environment in docker")

create_parser.add_argument("-n", "--name", help="This will be the name of the container. By default is ros-<distro>", required=False)
create_parser.add_argument("--ros-version",help="Version of ROS. Can be ROS2: humble, galactic, jazzy,... or even ROS1: noetic, melodic, ...\n If not specify the default distros humble", required=False)
create_parser.add_argument("-g", "--gazebo", help="Add all dependencies for using gzebo in the corresponding version", action="store_true", required=False)
create_parser.add_argument("-p", "--path", help="Specify a folder to copy with the ros environment. Most of the time is an existing source folder. If not defined an empty folder named 'ros_ws' will be create.", required=False)
create_parser.add_argument("-s", "--shared", help="Share the folder created or specify by --path to the container", action="store_true")
create_parser.add_argument("-e", "--env", help="You can specify a list of environment variables from a .txt file. They will be added to the default environment variable.", required=False)
create_parser.add_argument("-d", "--dependencies", help="You probably need specific dependencies for your project. Add them with a list in a .txt file.", required=False)


create_from_parser = command_subparser.add_parser("create_from", help="laod a ros_env_param.yaml and create files from parameter saved in it.")
create_from_parser.add_argument("-f", "--file", help="path to the file you want to load.", required=True)


delete_parser = command_subparser.add_parser("delete", help="Delete created file for ros environment in docker. Dockerfile, docker-compose.yaml, .env. And rm all docker contianers and images.")
build_parser = command_subparser.add_parser("build", help="Build the image. WARN: Need to be execute after the create commands")
start_parser = command_subparser.add_parser("start", help="Start the containers. From the corresponding image")
stop_parser = command_subparser.add_parser("stop", help="Stop the containers.")
kill_parser = command_subparser.add_parser("kill", help="Kill the containers wihtout removing the image.")




if __name__=="__main__":

    # Print the help if no command are given
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Analyser les arguments
    args = parser.parse_args()

    if args.command == "create":
        print(f"You have chosen ROS {args.ros_version} with the following option: ")
        print(f"\tContainer name: {args.name}")
        print(f'\tGazebo : {args.gazebo}')
        if args.shared: print(f'\tshared folder : {args.path}')
        else: print(f'\tcopy folder : {args.path}')
        print(f'\tenvironment variables : {args.env}')
        print(f'\tDependencies : {args.dependencies}')

        gen=docker_generator(args.name, args.gazebo, args.path, args.shared, args.env, args.dependencies, args.ros_version)

        RosEnvParam.generate(args.param_path, gen)

    elif args.command == "create_from":
        print(f"Load param from {args.file}")
        rosEnv = RosEnvParam.load(args.file)

        gen = docker_generator(rosEnv['image_name'],
                        rosEnv['option']["gazebo"],
                        rosEnv['option']['volume path'],
                        rosEnv['option']['volume shared'],
                        rosEnv['option']['additionnal']['Environment']['path'],
                        rosEnv['option']['additionnal']['dependencies']['path'],
                        rosEnv["ros"]['distro'])

        RosEnvParam.generate(args.param_path, gen)

    elif args.command == "delete":
        rosEnv = RosEnvParam.load(args.param_path)

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
        if docker_tools.isRunning(rosEnv['container_name']):
            if docker_tools.stop(rosEnv['container_name']) and docker_tools.rm(rosEnv['container_name']):
                print("Isolate environment killed.")
        elif docker_tools.exist(rosEnv['container_name']):
            if docker_tools.rm(rosEnv['container_name']):
                print("Isolate environment killed.")

        print("Deleting images:")
        docker_tools.rmi(rosEnv["image_name"])
        print("Delete completed !")

    elif args.command == "build":
        docker_tools.build()

    elif args.command == "start":
        # if never start: docker compose up -d else: docker start and open the bash terminal (without forgetting xhost +)
        rosEnv = RosEnvParam.load(args.param_path)

        if docker_tools.isRunning(rosEnv['container_name']): # If is already running
            print("Already start ! ")

        elif docker_tools.exist(rosEnv['container_name']):
            print("Already exist so start it")
            docker_tools.start(rosEnv['container_name'])

        else: # Does not exist so we create it 
            print("Doesn't exist ! Creation ...")
            process = subprocess.Popen("docker compose up -d", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Read the output in real-time
            for line in process.stdout:
                print(line.strip())
            return_code = process.wait()

        #Connect the terminal stream to the docker
        print("Connection to isolate environment ...")
        docker_tools.attachTerminal(rosEnv['container_name'])
        print("Exit of the isolate environment.\nHave a nice day ! ;)")

    elif args.command == "stop":
        rosEnv = RosEnvParam.load(args.param_path)

        if docker_tools.isRunning(rosEnv['container_name']): # If is already running
            docker_tools.stop(rosEnv['container_name'])
        else:
            print("Already stopped or maybe doesn't exist.")

    elif args.command == "kill":
        # docker stop and docker rm
        rosEnv = RosEnvParam.load(args.param_path)

        if docker_tools.isRunning(rosEnv['container_name']):
            if docker_tools.stop(rosEnv['container_name']) and docker_tools.rm(rosEnv['container_name']):
                print("Isolate environment killed.")
        elif docker_tools.exist(rosEnv['container_name']):
            if docker_tools.rm(rosEnv['container_name']):
                print("Isolate environment killed.")
        else:
            print("Isolate environment already killed or has never existed.")




# BMAybe for listing of distro
        # # URL of the ROS distribution index
        # url = "https://raw.githubusercontent.com/ros/rosdistro/master/index-v4.yaml"

        # try:
        #     response = requests.get(url)
        #     response.raise_for_status()  # Raise an error for bad status codes
        #     data = yaml.safe_load(response.text)

        #     print("List of ROS versions:")
        #     for distro in sorted(data["distributions"]):
        #         print(distro, end=" | ")
        #     print('\n')
        # except requests.RequestException as e:
        #     print(f"Error fetching ROS versions: {e}")
        # except yaml.YAMLError as e:
        #     print(f"Error parsing YAML: {e}")