from starlette.templating import Jinja2Templates

from backend.app.service_manager import ServiceManager

service_manager_instance: ServiceManager = ServiceManager()


def service_manager() -> ServiceManager:
    """
    Get the service manager.
    :return: The service manager.
    """
    return service_manager_instance


templates_instance: Jinja2Templates = Jinja2Templates(directory="frontend/templates")


def templates() -> Jinja2Templates:
    """
    Get the Jinja template instance.
    :return: The Jinja template instance.
    """
    return templates_instance
