"""
Trading Signal Processing System - Main Entry Point
"""

import uvicorn
from rest_api import app


def main():
    """Main function to start the API server"""
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()
