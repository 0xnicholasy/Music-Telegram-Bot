def split_string(input_string):
    max_length = 4096
    if len(input_string) <= max_length:
        return [input_string]
    
    split_strings = []
    temp_string = ""
    code_block = False
    for line in input_string.split('\n'):
        # Check if line is a code block
        if line.strip().startswith('```'):
            code_block = not code_block

        if len(temp_string + line + '\n') > max_length and not code_block:
            split_strings.append(temp_string)
            temp_string = line + '\n'
        else:
            temp_string += line + '\n'
    
    if temp_string:
        split_strings.append(temp_string)
    
    return split_strings
