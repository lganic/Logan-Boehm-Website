from typing import Tuple, Dict

def find_all_occurences(string: str, substring: str):

    output = []

    base_index = 0

    while True:

        location = string.find(substring, base_index)

        if location == -1:
            return output
    
        output.append(location)

        base_index = location + len(substring)

def parse_block(string: str, from_substring: str, to_substring: str):

    s_lower = string.lower()

    location_a = s_lower.find(from_substring.lower())

    location_a += len(from_substring)

    location_b = s_lower.find(to_substring.lower(), location_a)

    return string[location_a: location_b]

def quasi_equal_at_location(string:str , location: int, key: str):
    '''
    Check if a string contains the key at location, irrespective of spaces and case
    '''

    if ' ' in key:
        raise ValueError('Spaces invalid for quasi equal')

    if string[location] == ' ':
        return False
    
    for index, key_value in enumerate(key):

        while string[location] == ' ':
            location += 1

            if location == len(string):
                return False

        if string[location].lower() != key_value.lower():
            return False

        if index == len(key) - 1:
            return True

        location += 1

        if location == len(string):
            return False
    
    return True

def quasi_find(string: str, substring: str, base_location = 0):
    '''
    Find the first instance of a substring that is quasi equal.

    Return -1 if not found
    '''

    for index in range(base_location, len(string) - len(substring) + 1):

        if quasi_equal_at_location(string, index, substring):
            return index
        
    return -1

def quasi_end_of_string(string: str, substring: str, start_of_string: int):

    end_char = substring[-1]

    index = start_of_string

    count = substring.count(substring[-1])

    for _ in range(count):

        index = string.find(end_char, index) + 1
    
    return index

def optional_block_targeting(string: str, base_location: int, block_targets: Dict[str, str]):

    # Find reverse block

    found_target = None

    while found_target is None:

        for block in block_targets:

            if quasi_equal_at_location(string, base_location, block.lower()):

                found_target = block

                break

        else:

            base_location -= 1

            if base_location == -1:
                raise IndexError('Blocks not found')
    
    # Find end of block

    end_block_location = quasi_find(string, block_targets[found_target].lower(), base_location + 1)

    if end_block_location == -1:
        raise IndexError('End of target block not found')
    
    return (base_location, quasi_end_of_string(string, block_targets[found_target], end_block_location))

def isolate_block(string: str, block: Tuple[int, int]):

    return string[block[0]: block[1]]

if __name__ == '__main__':

    blocks = {
            '<video': '</video>>>',
            '<img': '>',
        }

    testing_string = 'ABC< viDeo src yada> HEREsfjsjkdfhsjkdfh < /Video > > > >BC'
    testing_string_2 = 'ABC< IMG src yada> HEREsfjsjkdfhsjkdfh < /Video > > > >BC'

    start = testing_string.find('HERE')

    print(isolate_block(testing_string, optional_block_targeting(testing_string, start, blocks)))
    print(isolate_block(testing_string_2, optional_block_targeting(testing_string_2, start, blocks)))