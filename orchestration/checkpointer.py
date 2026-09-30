from langgraph.checkpoint.postgres import PostgresSaver
from core.config import settings
from contextlib import contextmanager

@contextmanager
def get_checkpointer()->PostgresSaver:
    connection_string=settings.database_url.replace("postgresql+psycopg://","postgresql://")
    with PostgresSaver.from_conn_string(connection_string) as checkpointer:
        yield checkpointer