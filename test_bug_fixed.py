def divide_numbers(a: float, b: float) -> float:
    """
    Return the result of dividing *a* by *b*.

    Raises:
        ValueError: If *b* is zero.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b


def main() -> None:
    x = 10
    y = 0   # <-- this would normally cause a ZeroDivisionError

    try:
        result = divide_numbers(x, y)
    except ValueError as exc:
        print(f"Error: {exc}")
    else:
        print("Result is:", result)


if __name__ == "__main__":
    main()