def calculator(expression: str):

    try:

        allowed = "0123456789+-*/(). "

        if not all(char in allowed for char in expression):
            return "Invalid expression"

        result = eval(expression)

        return result

    except Exception as e:

        return f"Calculation error: {e}"


# Test calculator
if __name__ == "__main__":

    result = calculator("15000 / 5 + 2500")

    print("\n====================================")
    print("          CALCULATOR TOOL")
    print("====================================")

    print("\nExpression: 15000 / 5 + 2500")
    print("Result:", result)

    print("\n====================================")
    print("      CALCULATION COMPLETED")
    print("====================================")