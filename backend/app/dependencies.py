from starlette.templating import Jinja2Templates

from backend.app.services import Services

services_instance: Services = Services()


def services() -> Services:
    """
    Get services.
    :return: The services.
    """
    return services_instance


templates_instance: Jinja2Templates = Jinja2Templates(directory="frontend/templates")


def templates() -> Jinja2Templates:
    """
    Get the Jinja template instance.
    :return: The Jinja template instance.
    """
    return templates_instance
