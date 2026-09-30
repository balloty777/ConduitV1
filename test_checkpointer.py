from orchestration.checkpointer import get_checkpointer

with get_checkpointer() as checkpointer:
    checkpointer.setup()
    print("Checkpoint tables initialized")