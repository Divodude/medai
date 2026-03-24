try:
    from api.main import app
except ImportError as e:
    print(f"Import Error: {e}")
    raise e

# This file serves as the Vercel entrypoint.
# It imports the FastAPI app from the backend package.
