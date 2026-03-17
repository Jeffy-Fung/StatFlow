import os

# Set required env vars before any app module is imported during test collection.
# This avoids a startup failure when SECRET_KEY is not present in the shell environment.
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
