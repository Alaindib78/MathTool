import os

import uvicorn

from api.app import app


if __name__ == "__main__":
    uvicorn.run(
        "run_api:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
    )
