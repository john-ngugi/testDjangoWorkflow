from pathlib import Path
import os


from split_settings.tools import include, optional

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


ENVAR_SETTINGS_PREFIX ='MTAAWETU_'

LOCAL_SETTINGS_PATH =os.getenv(f'{ENVAR_SETTINGS_PREFIX}LOCAL_SETTINGS_PATH')

if not LOCAL_SETTINGS_PATH :
    LOCAL_SETTINGS_PATH = 'C:/Users/hp/Documents/mtaawetu-tests/mtaawetutest/mtaawetu/local/settings.dev.py'

if not os.path.isabs(LOCAL_SETTINGS_PATH):
    LOCAL_SETTINGS_PATH = str(BASE_DIR/LOCAL_SETTINGS_PATH)

print(LOCAL_SETTINGS_PATH)
include(
    'base.py',
    'logging.py',
    'custom.py',
    optional(LOCAL_SETTINGS_PATH),
    'envars.py',
    'docker.py'
)
