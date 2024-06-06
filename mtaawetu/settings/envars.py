from mtaawetu.core.utils.collections import deep_update #type:ignore
from mtaawetu.core.utils.settings import get_settings_from_environment #type:ignore



deep_update(globals(),get_settings_from_environment(ENVAR_SETTINGS_PREFIX)) # type:ignore
