import yaml

class YamlGenerator:
    def generate_yaml(self, app_name: str, docker_image: str, port: int) -> str:
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": app_name},
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": {"app": app_name}},
                "template": {
                    "metadata": {"labels": {"app": app_name}},
                    "spec": {
                        "containers": [{
                            "name": app_name,
                            "image": docker_image,
                            "ports": [{"containerPort": port}]
                        }]
                    }
                }
            }
        }

        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": app_name},
            "spec": {
                "type": "LoadBalancer",
                "selector": {"app": app_name},
                "ports": [{
                    "protocol": "TCP",
                    "port": 80,
                    "targetPort": port
                }]
            }
        }

        return yaml.dump_all([deployment, service])
