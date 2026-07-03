"""Common test fixtures for the Hypothesis Factory project."""

import os
import sys
from pathlib import Path

# Add api_gateway/services root to PYTHONPATH to allow imports like 'src.main'
api_gateway_path = Path(__file__).resolve().parent.parent / "services" / "api_gateway"
if str(api_gateway_path) not in sys.path:
    sys.path.insert(0, str(api_gateway_path))

# Set test environment variables
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "True"
os.environ["CORS_ORIGINS"] = '["*"]'
