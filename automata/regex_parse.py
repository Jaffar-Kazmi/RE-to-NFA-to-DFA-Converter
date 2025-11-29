# automata/regex_parse.py

def precedence(op):
    if op == '+':
        return 1
    if op == '.':
        return 2
    if op == '*':
        return 3
    return 0

def add_concat_ops(regex: str) -> str:
    result = []
    prev = None
    for c in regex:
        if prev:
            if (prev.isalnum() or prev in (')', '*')) and (c.isalnum() or c == '('):
                result.append('.')
        result.append(c)
        prev = c
    return ''.join(result)

def to_postfix(regex: str) -> str:
    output = []
    stack = []
    for c in regex:
        if c.isalnum():
            output.append(c)
        elif c == '(':
            stack.append(c)
        elif c == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        else:
            if c == '*':
                while stack and precedence(stack[-1]) >= precedence(c):
                    output.append(stack.pop())
                stack.append(c)
            else:
                while stack and stack[-1] != '(' and precedence(stack[-1]) >= precedence(c):
                    output.append(stack.pop())
                stack.append(c)
    while stack:
        output.append(stack.pop())
    return ''.join(output)
