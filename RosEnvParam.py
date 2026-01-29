import yaml
import pathlib
from docker_generator import docker_generator

class RosEnvParam:

    def generate(name:str, gen: docker_generator) -> None:
        # Define your data as a Python dictionary
        data = {
            "image_name": gen.name,
            "container_name": gen.name,
            "ros": {
                "distro": gen.ros_distro,
                "type": gen.ros_type
            },
            "option":{
                "gazebo": gen.isGazebo,
                "volume shared": gen.isShared,
                "volume path list": gen.volumes_path_list,
                "additionnal":{
                    "dependencies":{
                        "status": gen.isDependencies,
                        "path": gen.dependencies_path if gen.isDependencies else None
                    },
                    "Environment":{
                        "status":gen.isEnv,
                        "path": gen.env_path if gen.isEnv else None
                    }
                }
            }
        }

        # Write the dictionary to a YAML file
        with open(name, "w") as file:
            yaml.dump(data, file, sort_keys=False, default_flow_style=False)
        print(name," file created")

    def exist(path: str) -> pathlib.Path:
        target = pathlib.Path(path)
        if target.is_file() and target.suffix == ".yaml":
            return target  
        raise FileExistsError(f"This path {path} doesn't lead to a .txt file.")


    def load(path: pathlib.Path):
        with open(path, "r") as param_file:
            ros_env_param = yaml.safe_load(param_file)
        return ros_env_param