import pathlib
import requests
import yaml
import os



class docker_generator():
    def __init__(self, name:str ,isGazebo:bool, volumes_path_list: list[str], isShared:bool, env_path, dependencies_path, ros_version: str):
        """
            This classe generate all necessary for a ros environment in a container.
    
        :param isGazebo: If you want to use Gazebo for simulation set True. All dependencies necessary will be install.
        :type isGazebo: bool
        :param volumes_path_list: List of path to folders you want to copy into the docker.
        :type volumes: list[str]
        :param isShared: If True the copy folder and the original one will be linked between your account and the docker environement.
        :type isShared: bool
        :param env_path: The path to a .txt file which contain all additionnal envrionment variable you want to set up.
        :param dependencies_path: The path to a .txt file which contain all additionnal dependencies you want to set up.
        :param ros_version: The version of the ros distro ex: humble, galactic, melodic, noetic
        :type ros_version: str
        """
        self.ros_version=ros_version if ros_version!=None else "humble"
        self.name=name if name!=None else "ros-"+self.ros_version
        self.isGazebo=isGazebo
        self.isShared=isShared

        self.isVolumes = volumes_path_list != None
        self.isEnv = env_path != None
        self.isDependencies = dependencies_path != None

        print("Checking for ROS version ...",)
        # URL of the ROS distribution index
        url = "https://raw.githubusercontent.com/ros/rosdistro/master/index-v4.yaml"

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad status codes
            data = yaml.safe_load(response.text)

        except requests.RequestException as e:
            print(f"Error fetching ROS versions: {e}")
        except yaml.YAMLError as e:
            print(f"Error parsing ROS YAML: {e}")
        
                
        if not self.ros_version in data["distributions"]:
            raise NameError(f"{self.ros_version} distro is not supported")
        # Get the type of the distro
        self.ros_type = "ros2" if data['distributions'][self.ros_version]['distribution_type'] == "ros2" else "ros"
        print(f"Distribution info :\n\tName: {self.ros_version}\n\tType: {self.ros_type}")

        
        print("ROS version checked!")
        # Check volumes
        if self.isShared and not self.isVolumes:
                print("Shared parameters is True but no Volumes path was given. A default folder will be created and shared.")
                self.isVolumes = True
                # Don't overwrite on an existing directory
                i=0
                while True:
                    try:
                        self.volumes_path_list = [f"./{self.ros_type}_ws"] if i==0 else [f"./{self.ros_type}_ws_{i}"]
                        os.mkdir(self.volumes_path_list[0]) # No path were given so we add into the list only one element that why we czn use [0]
                        break
                    except FileExistsError as e:
                        i+=1
                        continue
        elif self.isVolumes:
            self.volumes_path_list = volumes_path_list

        # Check environment
        if self.isEnv:
            print("Checking for environment Path ... ", end="")
            self.env_path = pathlib.Path(env_path)
            if not(isTXT(self.env_path)):
                raise FileNotFoundError("This file is weird. Please specify the path to a .txt file.")
            print("Done")

            print("Loading environment variable ... ", end="")
            self.env = self.load(self.env_path)
            print("Done")

        #Check dependencies
        if self.isDependencies:
            print("Checking for dependencies Path ... ", end="")
            self.dependencies_path = pathlib.Path(dependencies_path)
            if not(isTXT(self.dependencies_path)):
                raise FileNotFoundError("This file is weird. Please specify the path to a .txt file.")
            print("Done")

            print("Loading dependencies ... ", end="")
            self.dependencies = self.parseDependenciesString(self.load(self.dependencies_path))
            print("Done")
            
        # Generate Dockerfile
        print("Generating Dockerfile ... ", end="")
        self.generate_Dockerfile()
        print("Done")

        #generate .env file
        print("Generating .env file ... ", end="")
        self.generate_env_file()
        print("Done")

        #Generate docker-compose.yaml
        print("Generating docker-compose.yaml file ... ", end="")
        self.generate_docker_compose()
        print("Done")
        
    def generate_Dockerfile(self) -> None:
        with open("Dockerfile", mode="w") as Dockerfile:
            # Setting the based image
            Dockerfile.write(f"FROM osrf/ros:{self.ros_version}-desktop \n")

            # Download all dependencies
            Dockerfile.write("RUN apt-get update && apt-get install -y \\ \n")
            
            for DefaultDep in self.getDefaultDep():
                Dockerfile.write(f"\t{DefaultDep} \\ \n")
            
            for rosDep in self.getRosDep():
                Dockerfile.write(f"\t{rosDep} \\ \n")
            
            if self.isGazebo:
                for gzDep in self.getGazeboDep():
                    Dockerfile.write(f"\t{gzDep} \\ \n")
            
            if self.isDependencies:
                for addDep in self.dependencies["apt"]:
                    Dockerfile.write(f"\t{addDep} \\ \n")

            Dockerfile.write("\t&& rm -rf /var/lib/apt/lists/*\n\n")

            Dockerfile.write("RUN pip install --no-cache-dir \\ \n"
                             "\tnetworkx \\ \n"
                             "\tmatplotlib \\ \n"
                              "\txacro ")
            if self.isDependencies:
                for addDep in self.dependencies["pip"]:
                    Dockerfile.write(f"\\ \n\t{addDep}")

            if self.isGazebo: # Need to add until we have sudo permision in the docker
                if self.ros_type == "ros2":
                    Dockerfile.write("\n# Installing Dynamic World Generator for Gazebo world generation\n")
                    Dockerfile.write("RUN cd / && sudo git clone https://github.com/ali-pahlevani/Dynamic_World_Generator.git \n")
                    Dockerfile.write("RUN pip3 install PyQt5 lxml\n")
                    Dockerfile.write("# Remove .py extension to simplify the use\n")
                    Dockerfile.write("RUN sudo mv /Dynamic_World_Generator/code/dwg_wizard.py /Dynamic_World_Generator/code/dwg_wizard\n")
            
            
            Dockerfile.write("\n# Setting up the user of the docker\n")
            Dockerfile.write("ARG UID\n")
            Dockerfile.write("ARG GID\n")
            Dockerfile.write("ARG USER\n")
            Dockerfile.write("ARG GROUP\n")
            Dockerfile.write("RUN echo '$USER ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers\n")
            Dockerfile.write("RUN groupadd -g $GID $GROUP\n")
            Dockerfile.write("RUN useradd -ms /bin/bash -u $UID -g $GID $USER\n")
            Dockerfile.write("RUN adduser $USER dialout\n")
            Dockerfile.write("RUN addgroup $USER dialout\n")
            Dockerfile.write("RUN adduser $USER video\n")
            Dockerfile.write("RUN usermod -a -G video $USER\n")
            Dockerfile.write("USER $USER\n")

            Dockerfile.write("\n# Add the source command to .bashrc\n")
            Dockerfile.write(f"RUN echo 'source /opt/ros/{self.ros_version}"+"/setup.sh' >> /home/${USER}/.bashrc\n")

            if self.isGazebo and self.ros_type == "ros2":
                    Dockerfile.write("RUN echo 'export PATH=$PATH:/Dynamic_World_Generator/code/' >> /home/${USER}/.bashrc\n")
            
            if self.isVolumes:
                Dockerfile.write("\n# Copy your workspace into the home container\n")
                for volume in self.volumes_path_list:
                    volume = pathlib.Path(volume)
                    Dockerfile.write(f"COPY ./{volume.resolve().relative_to(pathlib.Path.cwd())} /home/${{USER}}/{volume.name}\n")
            else:
                Dockerfile.write("\n# Create your workspace into the container\n")
                Dockerfile.write(f"RUN mkdir /home/${{USER}}/{self.ros_type}_ws\n")

            Dockerfile.write(f"WORKDIR /home/${{USER}}/\n")

    def generate_env_file(self) -> None:
        """
        Description :
            Generate a cached file named .env. This file contain all environment variable we want to define in a Docker.
        returns: None
        """
        username = os.getlogin()  # Gets the login name of the current user
        uid = os.getuid()  # Gets the real user ID of the current process
        gid = os.getgid()  # Gets the real user group ID of the current process        

        # generate file
        with open("./.env", mode="w") as env_file:
            env_file.write("DISPLAY=:0\n"
                           "QT_X11_NO_MITSHM=1\n"
                           f"UID={uid}\n"
                           f"GID={gid}\n"
                           f"USER={username}\n"
                           f"GROUP={username}\n")

            
            if self.isEnv:
                env_file.write(f"\n{self.env}")

    def generate_docker_compose(self) -> None:
        data = {
            "version": '3.8',
            "services":{
                "gz_test":{
                    "container_name": self.name,
                    "image": self.name,
                    "build": {
                        "context": ".",
                        "dockerfile": "Dockerfile",
                        "args": {
                            "UID": "${UID}",
                            "GID": "${GID}",
                            "USER": "${USER}",
                            "GROUP": "${GROUP}"
                        }
                    },
                    "env_file": [".env"],

                    "volumes": ["/tmp/.X11-unix:/tmp/.X11-unix"],
                    "stdin_open": True,
                    "tty": True
                }
            }
        }

        if self.isShared:
            for volume in self.volumes_path_list:
                volume = pathlib.Path(volume)
                data["services"]["gz_test"]["volumes"].append(f"./{volume.resolve().relative_to(pathlib.Path.cwd())}:/home/${{USER}}/{volume.name}")

                # Write the dictionary to a YAML file
        with open("docker-compose.yaml", "w") as file:
            yaml.dump(data, file, sort_keys=False)


    
            
    def getRosDep(self) -> str:
        return [f"ros-{self.ros_version}-{self.ros_type}-control",
        f"ros-{self.ros_version}-{self.ros_type}-controllers",
        f"ros-{self.ros_version}-joint-state-publisher",
        f"ros-{self.ros_version}-diagnostic-updater",
        f"ros-{self.ros_version}-pcl-ros",
        f"ros-{self.ros_version}-xacro"]
    
    def getGazeboDep(self) -> str:
        if self.ros_type == "ros2":
            return [f"ros-{self.ros_version}-ros-gz-sim",
            f"ros-{self.ros_version}-gz-ros2-control",
            f"ros-{self.ros_version}-ros-gz-bridge",
            f"ros-{self.ros_version}-ros-gz-image"]
        else:
            return ["ros-noetic-gazebo-ros-pkgs", 
                    "ros-noetic-gazebo-ros-control"]
    
    def parseDependenciesString(self, str_dep:str):
        apt_dep = []
        pip_dep = []
        for line in str_dep.splitlines():
            if "#APT" in line:
                dep=apt_dep
            elif "#PIP" in line:
                dep=pip_dep
            elif line!="" and line[0] != "#":
                dep.append(line)       

        return {"apt": apt_dep, "pip": pip_dep}
                   
    def getDefaultDep(self) -> str:
        return ["git",
        "make",
        "cmake",
        "build-essential",
        "python3",
        "python3-pip",
        "python3-rosdep",
        "libglib2.0-0",
        "libsm6",
        "libxext6",
        "libxrender-dev",
        "libopencv-dev",
        "ffmpeg",
        "xterm"]
    
    def load(self, path:pathlib.Path) -> str:
        """
        Load the content of a file into a string variable. WARNING: No checkup of the existence of the file is done.
        
        :param path: the path to the file
        :type path: pathlib.Path
        :return: content of the file
        :rtype: str
        """
        with open(path, mode="r") as file:
            res = file.read()

        return res


def isTXT(path: pathlib.Path) -> bool:

    if not path.is_file():
        raise FileExistsError(f"This path {path} doesn't not exist. Please enter a path to .txt file.")
    
    if path.is_dir():
        raise FileNotFoundError(f"{path} is a DIRECTORY. Please enter a path to .txt file.")

    if path.suffix != ".txt":
        raise FileExistsError(f"This path {path} doesn't lead to a .txt file.")
    return True