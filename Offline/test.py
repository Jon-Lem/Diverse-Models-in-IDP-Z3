line = 'n := {s1 -> 5, s1 -> 6, s1 -> 5, s1 -> 5 }.'

line0 = line.strip('->')
print(line0)

line1 = line.split('->')[-1].split('}.')[0].strip()
print(line1)