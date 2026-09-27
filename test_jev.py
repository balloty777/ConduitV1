from services.jev_service import JevService
jev = JevService()
state = {
    "request": "Create a Diwali marketing campaign for our customers.",
}
questions = {
    "department": {
        "type": "choice",
        "instructions": "Which Conduit department should handle this request?",
        "criteria": {
            "marketing": "Marketing campaigns, content, audiences, and promotions.",
            "sales": "Leads, prospects, follow-ups, and sales activity.",
            "tech": "Technical tickets, bugs, fixes, and technical issues.",
        },
    }
}
result = jev.decide(state=state,questions=questions)

print("Department:", result.choice)
print("Confidence:", result.confidence)
print("Probabilities:", result.probabilities)