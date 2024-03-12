from backend.app.service_manager import ServiceManager

service_manager_instance: ServiceManager = ServiceManager()


def service_manager() -> ServiceManager:
    return service_manager_instance
