"""Common test fixtures for the API Gateway service."""

import os

# Set test environment variables
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "True"
os.environ["CORS_ORIGINS"] = '["*"]'
