def request_human_approval(action: str) -> bool:

    print("\n========================================")
    print("        HUMAN APPROVAL REQUIRED")
    print("========================================")

    print("\nThe AI wants to perform this action:")
    print("----------------------------------------")
    print(action)

    print("\nPlease choose:")

    print("1. Approve")
    print("2. Reject")

    while True:

        choice = input("\nEnter your choice (1/2): ").strip()

        if choice == "1":

            print("\n✅ Human approved the action.")
            return True

        elif choice == "2":

            print("\n❌ Human rejected the action.")
            return False

        else:

            print("Please enter only 1 or 2.")


# Test Human Approval
if __name__ == "__main__":

    approved = request_human_approval(
        "Delete 10 old records from the database."
    )

    if approved:

        print("\nAction can continue.")

    else:

        print("\nAction stopped.")