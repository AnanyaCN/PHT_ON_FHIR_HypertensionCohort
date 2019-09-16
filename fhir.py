from fhirclient import client
from datetime import datetime
from datetime import date
from fhirclient.models import fhirsearch
import pandas as pd
import numpy as np
import matplotlib
import seaborn

def perform_in(srch_str,server, apiBase):
    """ Execute the search URL against the given server.

    :param server: The server against which to perform the search
    :returns: A Bundle resource
    """

    from fhirclient.models import bundle
    if server is None:
        raise Exception("Need a server url to perform search")
    resources = []
    bundleBase = server.request_json(srch_str)
    bundleCur = bundleBase

    from fhirclient.models import bundle
    bundle = bundle.Bundle(bundleBase)
    bundle.origin_server = server
    if bundle is not None and bundle.entry is not None:
        for entry in bundle.entry:
            resources.append(entry.resource)
    return resources

## Run Cohort Analyser
def runCohortAnalyse(endpointUrl, endpointToken):

    #connect to FHIR server
    smart = client.FHIRClient(settings={
        'app_id': endpointToken,
        'api_base': endpointUrl
    })

    search_str = 'Condition?_include=Condition:patient&code=http://snomed.info/sct|38341003'+ '&_count=300' + endpointToken
    cohort_2 = perform_in(search_str, smart.server, endpointUrl)

    results = len(cohort_2)
    cohortSize = int(results / 2)

    col_names = ['age','gender','bmi_value']
    data = pd.DataFrame(columns=col_names)

    def calculate_age(born):
        # convert str to datetime format
        dob = datetime.strptime(born, "%Y-%m-%d")
        today = date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    # Loop over all patients in bundle
    for patients in cohort_2:
        entry = patients.as_json()
        if entry['resourceType']=="Patient":
            patient_gender = entry['gender']
            patient_id = entry['id']
            # srch_diabetes = 'Condition?subject='+patient_id+'&code=http://snomed.info/sct|73211009&_count=1'+endpointToken
            # bundle_diabetes = perform_in(srch_diabetes, smart.server, endpointUrl)
            # for diabetes_entries in bundle_diabetes:
            #     print(diabetes_entries.as_json())
            # if len(bundle_diabetes) > 0:
            #     diabetes_present = True
            # else:
            #     diabetes_present = False
            srch_bmi = 'Observation?subject='+patient_id+'&category=http://hl7.org/fhir/observation-category|vital-signs&code=http://loinc.org|39156-5&_count=1'+endpointToken
            bmi_bundle = perform_in(srch_bmi,smart.server, endpointUrl)
            for bmi_entries in bmi_bundle:
                bmi_resource=bmi_entries.as_json()
                bmi_val= bmi_resource['valueQuantity']['value']
            if 'birthDate' in entry.keys():
                dob = entry['birthDate']
                age_i = calculate_age(dob)
            else:
                results = results - 1
            data_dict = {'age': age_i, 'gender':patient_gender,'bmi_value': bmi_val}
            data = data.append(data_dict, ignore_index= True)
        else:
            results = results - 1
    data.to_csv('example_data.csv')

    meanAge = data["age"].mean()
    meanBmi = data["bmi_value"].mean()

    import matplotlib.pyplot as plt
    import seaborn as sns
    plot = sns.pairplot(x_vars=["age"], y_vars=["bmi_value"], data=data, hue="gender", height=5)
    plt.show()
    #image = plot.savefig('plot.png')

    # import base64
    # image = base64.encodebytes(plot).decode("utf-8")

    return {
        'cohortCount for Hypertension': results,
        'meanAge of cohort':meanAge,
        'meanBmi of cohort':meanBmi,
        }