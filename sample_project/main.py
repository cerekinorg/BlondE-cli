from utils import add, divide
from config import SETTINGS

def main():
    x = 10
    y = 0   # ⚠️ Bug: division by zero
    print("Sum:", add(x, y))
    try:
        division_result = divide(x, y)
    except ZeroDivisionError:
        division_result = "Error: division by zero"
    print("Division:", division_result)

    # Using config
    print("App name:", SETTINGS["app_name"])

if __name__ == "__main__":
    main()