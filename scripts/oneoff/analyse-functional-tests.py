import json
with open(file='/Users/gideongoldberg/Downloads/functional_20test_20report/report.json') as file:
  report = json.load(file)
  elements = (report[0]['elements'][0]['after'][0]['result']['duration'])
