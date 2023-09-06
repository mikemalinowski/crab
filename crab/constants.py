import os
import logging

# --------------------------------------------------------------------------------------
log = logging.getLogger("crab")

# --------------------------------------------------------------------------------------
PLUGIN_LOCATIONS = [
    os.path.join(
        os.path.dirname(__file__),
        "plugins",
    ),
]


# --------------------------------------------------------------------------------------
PLUGIN_ENVIRONMENT_VARIABLE = "CRAB_PLUGIN_PATHS"
