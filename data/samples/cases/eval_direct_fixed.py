import ast


def parse_value(user_text):
    return ast.literal_eval(user_text)
