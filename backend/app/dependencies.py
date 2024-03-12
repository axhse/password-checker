from backend.app.service_manager import ServiceManager

service_manager_instance: ServiceManager = ServiceManager()


def service_manager() -> ServiceManager:
    """
    Get the service manager.
    :return: The service manager.
    """
    return service_manager_instance
