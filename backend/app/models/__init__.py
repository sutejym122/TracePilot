"""Import every model here so that `Base.metadata` is fully populated.

Alembic's autogenerate and `Base.metadata.create_all` both rely on all models
being imported. Phase 3 uncomments these as each model is implemented.
"""
from app.models.base import TimestampMixin, uuid_pk  # noqa: F401

# TODO(phase3): uncomment as each model is implemented.
from app.models.user import User  # noqa: F401
from app.models.service import Service  # noqa: F401
from app.models.health import HealthCheck  # noqa: F401
# from app.models.metric import ApiMetric  # noqa: F401
from app.models.release import Release, ReleaseChecklist  # noqa: F401
from app.models.incident import Incident  # noqa: F401