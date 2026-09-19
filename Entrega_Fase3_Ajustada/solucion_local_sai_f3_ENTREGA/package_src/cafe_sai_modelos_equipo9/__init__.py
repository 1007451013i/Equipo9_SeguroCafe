__version__ = "0.1.0"

from .loader import get_models_dir, set_models_dir, load_models, load_reference_csv
from .schemas import (
    Departamento,
    FEATURES_FENOLOGICAS,
    TARGET,
    RendimientoFeatures,
    ActivacionSPIInput,
    RendimientoPredictionOutput,
    ActivacionSPIOutput,
)
from .track_b_rendimiento import predict_rendimiento
from .track_a_spi import predict_activacion_spi
from .kpis import (
    get_kpis_track_b,
    get_kpis_track_a,
    get_kpis_actuariales,
    list_kpis_available,
)
from .panel import (
    get_panel_entrenamiento,
    get_pred_vs_real_loyo,
    get_validacion_historica_n1,
)

__all__ = [
    "__version__",
    "get_models_dir",
    "set_models_dir",
    "load_models",
    "load_reference_csv",
    "Departamento",
    "FEATURES_FENOLOGICAS",
    "TARGET",
    "RendimientoFeatures",
    "ActivacionSPIInput",
    "RendimientoPredictionOutput",
    "ActivacionSPIOutput",
    "predict_rendimiento",
    "predict_activacion_spi",
    "get_kpis_track_b",
    "get_kpis_track_a",
    "get_kpis_actuariales",
    "list_kpis_available",
    "get_panel_entrenamiento",
    "get_pred_vs_real_loyo",
    "get_validacion_historica_n1",
]
