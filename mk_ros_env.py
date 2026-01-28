#!/usr/bin/env python3

import argparse
import os
from docker_generator import docker_generator
import sys

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

        print("Deleting docker container ...")
            # TODO: fetch name of the containers and run docker stop <contianers_name> and run docker rm <containers_name>
        print("Container deleted.")
        print("Deleting images ...")
            # TODO: fetch name of the image and run docker rmi <image_name>
        print("Images deleted.")
        print("Delete completed !")

    elif args.command == "build":
        # TODO: run docker compose build
        print("not emplemented yet.")
    elif args.command == "start":
        # TODO: if never start: docker compose up -d else: docker start and open the bash terminal (without forgetting xhost +)
        print("not emplemented yet.")
    elif args.command == "stop":
        # TODO: docker stop
        print("not emplemented yet.")
    elif args.command == "kill":
        # TODO: docker stop and docker rm
        print("not emplemented yet.")