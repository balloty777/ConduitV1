from orchestration.nodes.router import router_node


state = {
    "request": "What are the sales lead currenly?",
    "user_id": None,
    "execution_id": None,
    "workflow": None,
    "confidence": None,
    "status": "running",
    "current_node": None,
    "subject_type": None,
    "subject_id": None,
    "approval_request_id": None,
    "approval_reason": None,
    "output": None,
    "error": None,
}

result = router_node(state)

print("Workflow:", result["workflow"])
print("Confidence:", result["confidence"])
print("Current node:", result["current_node"])
print("Status:", result["status"])