from datetime import datetime, timezone

import docker


def get_docker_containers(base_url: str = None) -> dict:
    """List containers from the configured Docker Engine."""
    checked_at = datetime.now(timezone.utc).isoformat()
    try:
        client = docker.DockerClient(base_url=base_url) if base_url else docker.from_env()
        containers = client.containers.list(all=True)
        container_list = [
            {
                "id": container.short_id,
                "name": container.name,
                "image": container.image.tags[0] if container.image.tags else container.image.id[:12],
                "status": container.status,
                "created": container.attrs.get("Created"),
            }
            for container in containers
        ]
        return {
            "status": "Success",
            "total_containers": len(container_list),
            "containers": container_list,
            "error_code": None,
            "error": None,
            "checked_at": checked_at,
        }
    except Exception:
        return {
            "status": "Error",
            "total_containers": 0,
            "containers": [],
            "error_code": "DOCKER_CONNECTION_FAILED",
            "error": "Could not query the Docker Engine; check its availability and access permissions.",
            "checked_at": checked_at,
        }
