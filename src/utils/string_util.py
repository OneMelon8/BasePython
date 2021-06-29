def quote_join(messages):
    """
    Join together an iterable with each item sandwiched in quotes

    Args:
        messages (iterable): iterable of strings

    Returns:
        str: joined string
    """
    output = ""
    for message in messages:
        output += f"\"{message}\", "
    return output[:-2]
