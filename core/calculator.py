import math
import re

def safe_calculate(expression: str) -> str:
    try:
        # Clean karo expression
        expr = expression.strip()
        expr = expr.replace("x", "*")
        expr = expr.replace("×", "*")
        expr = expr.replace("÷", "/")
        expr = expr.replace("^", "**")
        expr = expr.replace(",", "")

        # Safe math functions
        safe_dict = {
            "abs": abs, "round": round,
            "sqrt": math.sqrt, "pow": math.pow,
            "sin": math.sin, "cos": math.cos,
            "tan": math.tan, "log": math.log,
            "log10": math.log10, "pi": math.pi,
            "e": math.e, "floor": math.floor,
            "ceil": math.ceil, "factorial": math.factorial,
        }

        # Sirf safe characters allow karo
        allowed = re.compile(r'^[\d\s\+\-\*\/\.\(\)\%\*\,]+$')
        is_simple = bool(allowed.match(expr))

        if is_simple:
            result = eval(expr)
        else:
            result = eval(expr, {"__builtins__": {}}, safe_dict)

        # Result format karo
        if isinstance(result, float):
            if result == int(result):
                result = int(result)
            else:
                result = round(result, 6)

        return f"🧮 {expression} = {result}"

    except ZeroDivisionError:
        return "❌ Zero se divide nahi kar sakte!"
    except Exception as e:
        return f"❌ Calculation error: {str(e)}"

def is_math_query(message: str) -> bool:
    message_lower = message.lower()

    # Direct math symbols
    math_symbols = ["+", "-", "*", "/", "^", "√", "×", "÷"]
    if any(s in message for s in math_symbols):
        # Check karo numbers bhi hain
        if any(c.isdigit() for c in message):
            return True

    # Math keywords
    math_keywords = [
        "calculate", "calculate karo", "kitna hai",
        "calculate", "hisab", "jodo", "ghatao",
        "multiply", "divide", "plus", "minus",
        "square root", "sqrt", "factorial",
        "percent", "percentage", "power",
        "sin", "cos", "tan", "log",
        "barabar", "equals", "sum of",
        "product of", "kya hoga"
    ]
    return any(keyword in message_lower for keyword in math_keywords)

def extract_and_calculate(message: str) -> str:
    message_lower = message.lower()

    # Percentage calculate karo
    percent_match = re.search(
        r'(\d+(?:\.\d+)?)\s*(?:percent|%)\s+(?:of|ka|ka kitna)\s+(\d+(?:\.\d+)?)',
        message_lower
    )
    if percent_match:
        p = float(percent_match.group(1))
        n = float(percent_match.group(2))
        result = (p / 100) * n
        return f"🧮 {p}% of {n} = {result}"

    # Square root
    sqrt_match = re.search(
        r'(?:sqrt|square root|√)\s*(?:of\s*)?(\d+(?:\.\d+)?)',
        message_lower
    )
    if sqrt_match:
        n = float(sqrt_match.group(1))
        result = round(math.sqrt(n), 6)
        return f"🧮 √{n} = {result}"

    # Factorial
    fact_match = re.search(
        r'(\d+)\s*(?:factorial|!)',
        message_lower
    )
    if fact_match:
        n = int(fact_match.group(1))
        if n > 20:
            return "❌ Bahut bada number hai factorial ke liye!"
        result = math.factorial(n)
        return f"🧮 {n}! = {result}"

    # Simple math expression dhundo
    expr_match = re.search(
        r'(\d+(?:\.\d+)?)\s*([\+\-\*\/\^x×÷])\s*(\d+(?:\.\d+)?)',
        message
    )
    if expr_match:
        return safe_calculate(
            f"{expr_match.group(1)} {expr_match.group(2)} {expr_match.group(3)}"
        )

    # Pure expression
    pure_match = re.search(
        r'[\d\s\+\-\*\/\.\(\)\%\^]+',
        message
    )
    if pure_match:
        expr = pure_match.group().strip()
        if len(expr) > 2 and any(c.isdigit() for c in expr):
            return safe_calculate(expr)

    return ""