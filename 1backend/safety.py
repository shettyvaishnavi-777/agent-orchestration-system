def requires_human_approval(task: str) -> bool:

    sensitive_words = [
        "delete",
        "remove",
        "transfer money",
        "send money",
        "payment",
        "database deletion",
        "send email",
        "external communication"
    ]

    task_lower = task.lower()

    for word in sensitive_words:

        if word in task_lower:
            return True

    return False