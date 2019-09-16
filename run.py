import json


baseURl_syntheticMass = "https://syntheticmass.mitre.org/v1/fhir/"
apikey_syntheticMass = "&apikey=cMEml0Gs1o2uX9WhRcEVcVKYg97OnHgI"


import fhir as fhir
outputJson_syntheticMass = fhir.runCohortAnalyse(endpointUrl= baseURl_syntheticMass, endpointToken=apikey_syntheticMass)

# Write output to file
with open('output.txt', 'w') as f:
    f.write(json.dumps(outputJson_syntheticMass))

