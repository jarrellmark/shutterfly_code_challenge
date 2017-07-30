from main import Ingest
from main import TopXSimpleLTVCustomerEvents

import json
from pprint import pprint

D = {}

with open('../../input/input.txt', 'r') as input_file:
    input = json.load(input_file)
    for event in input:
        Ingest(event, D)

print("D:")
print("")
pprint(D)
print("")

top_10_ltvs = TopXSimpleLTVCustomerEvents(10, D)

print("top_10_ltvs:")
print("")
pprint(top_10_ltvs)
print("")

with open('../../output/output.txt', 'w') as output_file:
    output = json.dumps(
        top_10_ltvs,
        indent=2,
        separators=(',', ': '))
    output_file.write(output)
