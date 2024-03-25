# import re
# goal = "queen"
# original_string =  " queen := {(s1, 1, 4), (s1, 2, 1), (s1, 3, 5), (s1, 4, 2), (s1, 5, 6), (s1, 6, 3), (s1, 7, 7), (s2, 1, 6), (s2, 2, 4), (s2, 3, 2), (s2, 4, 7), (s2, 5, 5), (s2, 6, 3), (s2, 7, 1)}."

# # Remove unnecessary characters and split into individual tuples
# tuples = original_string.replace(goal+" := {", "").replace(")}.", "").split("), ")

# # Format each tuple into the desired format
# formatted_tuples = [f"{goal}{t[0]},{t[1]}, {t[2]})" for t in [tuple(pair.split(", ")) for pair in tuples]]

# # Join the formatted tuples with "&" and enclose them in parentheses
# result = " & ".join(formatted_tuples)
# result = result + "."

# print(result)

import re

goal = "queen"
original_string = " queen := {(s1, 1, 4), (s1, 2, 1), (s1, 3, 5), (s1, 4, 2), (s1, 5, 6), (s1, 6, 3), (s1, 7, 7), (s2, 1, 6), (s2, 2, 4), (s2, 3, 2), (s2, 4, 7), (s2, 5, 5), (s2, 6, 3), (s2, 7, 1)}."

# Use regular expression to find tuples within parentheses
tuples_pattern = re.compile(r'\((.*?)\)')
tuples = tuples_pattern.findall(original_string)
print(tuples)

formatted_tuples = [f"{goal}({t})" for t in tuples]
print(formatted_tuples)
result = " & ".join(formatted_tuples)
result = result + "."

print(result)




exit()

color = "ColourOf : (solution * country) -> color"



def print_line_starting_with(filename, word):
    with open(filename, 'r') as file:
        for line in file:
            if line.lstrip().startswith(word):
                print(line.rstrip())  # rstrip() removes any trailing newline characters
                return line.rstrip()
# Example usage:
filename = 'test.txt'  # Replace 'your_file.txt' with the path to your file
word = 'ColourOf'  # Replace 'example_word' with the word you're looking for

print(f"Lines starting with '{word}':")
color = print_line_starting_with(filename, word)

lastword = re.search(r"\s*([\S]+)$",color)
print(lastword.group())