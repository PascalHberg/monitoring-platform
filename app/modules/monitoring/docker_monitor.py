import docker

def get_docker_containers(base_url: str = None) -> dict:
    """
    Fragt laufende und gestoppte Docker-Container über die Docker Engine API ab.
    Standardmäßig greift es auf den lokalen Socket/Pipe zu.
    """
    try:
        # Greift lokal oder über eine entfernte URL (z. B. tcp://host:2375) zu
        if base_url:
            client = docker.DockerClient(base_url=base_url)
        else:
            client = docker.from_env()

        containers = client.containers.list(all=True)
        container_list = []

        for container in containers:
            container_list.append({
                "id": container.short_id,
                "name": container.name,
                "image": container.image.tags[0] if container.image.tags else container.image.id[:12],
                "status": container.status,
                "created": container.attrs.get("Created")
            })

        return {
            "status": "Success",
            "total_containers": len(container_list),
            "containers": container_list
        }
    except Exception as e:
        return {
            "status": "Error",
            "error": str(e)
        }