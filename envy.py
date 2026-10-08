import os

import dotenv

dotenv.load_dotenv()

# TODO (glowo): this is a bad design!
ADMIN_USERNAME = "glowo"

NEO4J_URI = os.environ["NEO4J_URI"]
NEO4J_USERNAME = os.environ["NEO4J_USERNAME"]
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]

NEO4J_CREDENTIALS = {
    "uri": NEO4J_URI,
    "username": NEO4J_USERNAME,
    "password": NEO4J_PASSWORD,
}

JWT_ALGORITHM = os.environ["JWT_ALGORITHM"]
JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]

GOOGLE_OAUTH_CLIENT_ID = os.environ["GOOGLE_OAUTH_CLIENT_ID"]
GOOGLE_OAUTH_CLIENT_SECRET = os.environ["GOOGLE_OAUTH_CLIENT_SECRET"]

FALKORDB_USERNAME = os.environ["FALKORDB_USERNAME"]
FALKORDB_PASSWORD = os.environ["FALKORDB_PASSWORD"]
FALKORDB_HOST = os.environ["FALKORDB_HOST"]
FALKORDB_PORT = int(os.environ["FALKORDB_PORT"])

FALKORDB_CREDENTIALS = {
    "username": FALKORDB_USERNAME,
    "password": FALKORDB_PASSWORD,
    "host": FALKORDB_HOST,
    "port": FALKORDB_PORT,
}

WFORUM_MCP_URL = os.environ["WFORUM_MCP_URL"]
