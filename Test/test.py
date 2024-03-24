def insert_empty_line_and_write(filename, position, text_to_write):
    # Read the content of the file
    with open(filename, 'r') as file:
        lines = file.readlines()

    for index,line in enumerate(lines):
        if line.strip().startswith("theory"):
            position =index+1

    # Insert an empty line at the specified position
    lines.insert(position, '\n')  # Adjust position to 0-based index

    # Write the text to the empty line
    lines[position] = text_to_write + '\n'  # Adjust position to 0-based index

    # Write the modified content back to the file
    with open(filename, 'w') as file:
        file.writelines(lines)

def undo_insert_empty_line_and_write(filename, position):
    # Read the content of the file
    with open(filename, 'r') as file:
        lines = file.readlines()

    # Check if the line at the specified position is an empty line
    if lines[position - 1].strip() == '':
        # Remove the empty line and the text written on it
        del lines[position - 1]
        del lines[position - 1]

        # Write the modified content back to the file
        with open(filename, 'w') as file:
            file.writelines(lines)
    else:
        print("Error: No empty line with text found at the specified position.")

# Example usage:
filename = 'test.txt'  # Replace 'example.txt' with the path to your file
position = 5  # Specify the position where you want to insert the empty line
text_to_write = 'This is some text to write on the empty line'

insert_empty_line_and_write(filename, position, text_to_write)
undo_insert_empty_line_and_write(filename, position)
