from contextlib import contextmanager
from langgraph.checkpoint.postgres import PostgresSaver
from core.config import settings

@contextmanager
def get_checkpointer() -> PostgresSaver:
    connection_string = settings.database_url.replace("postgresql+psycopg://","postgresql://")
    with PostgresSaver.from_conn_string(connection_string) as checkpointer:
        checkpointer.setup()
        yield checkpointer