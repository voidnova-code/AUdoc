from django.apps import AppConfig


class AppConfig(AppConfig):
    name = "app"

    def ready(self):
        import app.signals  # noqa: F401

        # Start the appointment confirmation scheduler
        try:
            from app.scheduler import start_scheduler
            start_scheduler()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not start scheduler: {str(e)}")
