# Make ROS Environment

This project is here to simplify the set up of an isolated ros evironment in containers. This support all ros distro from ROS1 and ROS2. You can do simlation with th corresponding version of gazebo.

## Dependencies

### System Dependencies

- Docker
- Docker compose
- Python

### Pip dependencies

- Pathlib
- argparse
- request
- yaml

## Usage


This script create the Dockerfile, thdocker-compose.yaml, the .env file.

By default it create a ROS Humble container with a folder /ros_ws

```bash
./mk_ros_env.py
```

You can specify a folder to copy in it:

```bash
./mk_ros_env.py --path ./path/to/your/folder/
```

You can specify the name of the image

```bash
./mk_ros_env --name my_ros_docker
```

And you can see more about with:

```bash
./mk_ros_env --help
```
