import re

colour_pattern = r"(\w+) -> (\w+)"
line = """

ColourOf := {Albania -> Red, Austria -> Red, Belarus -> Red, Belgium -> Red, Bosnia_and_Herzegovina -> Red, Bulgaria -> Yellow, Croatia -> Red, Czechia -> Yellow, Denmark -> Red, Estonia -> Red, Finland -> Red, France -> Red, Germany -> Red, Greece -> Red, Hungary -> Red, Iceland -> Red, Ireland -> Red, Italy -> Red, Kosovo -> Red, Latvia -> Red, Lithuania -> Red, Luxembourg -> Red, Netherlands -> Red, Norway -> Green, Macedonia -> Red, Montenegro -> Red, Moldova -> Red, Poland -> Red, Portugal -> Red, Romania -> Red, Russia -> Red, Serbia -> Red, Slovakia -> Red, Slovenia -> Red, Spain -> Red, Sweden -> Red, Switzerland -> Red, Ukraine -> Red, UK -> Red}.


"""
match = re.findall(colour_pattern, line)

print("match:",match)



pattern = '[a-z]+'
string = '-----2344-Hello--World!'
result = re.finditer(pattern, string)
print(result)