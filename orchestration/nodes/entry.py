from orchestration.state import State


def entry_node(state: State) -> State:
    return {**state,"current_node": "entry","status": "running"}