import requests

BASE_URL = "https://envotrack.com/api/1.1/obj"
API_KEY = "7475aebe1a2505a2a0581b0c24b48562"

DATA_TYPES = {
    "Business": "Business",
    "Chemical Inventory": "Chemical Inventory",
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

def fetch_data(data_type):
    all_data = []
    cursor = None
    while True:
        url = f"{BASE_URL}/{data_type}"
        if cursor:
            url += f"?cursor={cursor}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            break
        try:
            data = response.json()
        except ValueError as e:
            print(f"Error parsing JSON: {e}")
            break
        all_data.extend(data.get("response", {}).get("results", []))
        cursor = data["response"].get("cursor")
        if not cursor:
            break
    return all_data

def get_final_json():
    business_data = fetch_data(DATA_TYPES["Business"])
    chemical_inventory_data = fetch_data(DATA_TYPES["Chemical Inventory"])
    business_dict = {biz["_id"]: biz for biz in business_data}

    final_json = {"reportyear": 2019, "facilities": []}

    for chem in chemical_inventory_data:
        business_id = chem.get("business")
        if business_id in business_dict:
            business = business_dict[business_id]
            
            # Add dummy values where data might be missing
            emergency_contacts = [
                {
                    "firstName": "DummyFirstName",
                    "lastName": "DummyLastName",
                    "title": "DummyTitle",
                    "email": "dummy@example.com",
                    "mailingAddress": {
                        "street": "DummyStreet",
                        "city": "DummyCity",
                        "state": "DummyState",
                        "zipcode": "00000",
                        "country": "DummyCountry"
                    },
                    "contactTypes": ["DummyContactType"],
                    "phones": [
                        {
                            "phoneNumber": "000-000-0000",
                            "phoneType": "DummyType"
                        }
                    ],
                    "lastModified": "2000-01-01"
                }
            ]
            
            facility = {
                "recordid": chem.get("_id", "DummyRecordID"),
                "facilityName": business.get("name", "DummyFacilityName"),
                "streetAddress": {
                    "street": business.get("street", "DummyStreet"),
                    "city": business.get("city", "DummyCity"),
                    "state": business.get("state", "DummyState"),
                    "zipcode": business.get("zip", "00000")
                },
                "mailingAddress": {
                    "street": business.get("mailing_address", {}).get("street", "DummyStreet"),
                    "city": business.get("mailing_address", {}).get("city", "DummyCity"),
                    "state": business.get("mailing_address", {}).get("state", "DummyState"),
                    "zipcode": business.get("mailing_address", {}).get("zipcode", "00000"),
                    "country": business.get("mailing_address", {}).get("country", "DummyCountry")
                },
                "county": business.get("county", "DummyCounty"),
                "fireDistrict": business.get("FireDistrict", "DummyFireDistrict"),
                "latLong": {
                    "latitude": business.get("latitude", 0.0),
                    "longitude": business.get("longitude", 0.0)
                },
                "department": business.get("Department", "DummyDepartment"),
                "notes": business.get("Notes", "DummyNotes"),
                "sitePlanAttached": business.get("site plan attached", False),
                "siteCoordAbbrevAttached": business.get("site coordinate abbreviation", False),
                "dikeDescriptionAttached": business.get("dike description attached", False),
                "facilityInfoSameAsLastYear": business.get("info_same_as_last_year", False),
                "nameAndTitleOfCertifier": business.get("certifier name", "DummyCertifier"),
                "dateSigned": business.get("date signed", "2000-01-01"),
                "feesTotal": business.get("fees total", 0.0),
                "phone": {
                    "phoneNumber": business.get("phone", "000-000-0000"),
                    "phoneType": business.get("phoneType", "DummyPhoneType")
                },
                "manned": business.get("manned", False),
                "maxNumOccupants": business.get("max no. of occupants", 0),
                "subjectToChemAccidentPrevention": business.get("subject to chemical prevention", False),
                "subjectToEmergencyPlanning": business.get("emergency planning", False),
                "LEPC": business.get("LEPC", "DummyLEPC"),
                "contactIds": business.get("contacts", []),
                "stateFields": [
                    {
                        "label": "DummyLabel",
                        "t2sFieldname": "DummyFieldName",
                        "data": "DummyData"
                    }
                ],
                "facilityIds": [
                    {
                        "recordid": "DummyRecordID",
                        "type": "NAICS",
                        "id": "123456",
                        "description": "DummyDescription"
                    }
                ],
                "lastModified": business.get("last modified", "2000-01-01"),
                "chemicals": [{
                    "chemName": chem.get("Product Name", "DummyChemical"),
                    "casNumber": chem.get("Product Code/CAS", "000-00-0"),
                    "ehs": chem.get("is it EHS (extremely hazardous)?", False),
                    "pure": chem.get("Pure or Mixt.", "") == "Pure",
                    "mixture": chem.get("Pure or Mixt.", "") == "Mixture",
                    "solid": chem.get("Solid", False),
                    "liquid": chem.get("Liquid", False),
                    "gas": chem.get("Gas", False),
                    "hazards": [{
                        "category": "DummyHazardCategory",
                        "value": False
                    }],
                    "aveAmount": chem.get("Average Daily Amount Stored(pounds)", 0),
                    "aveAmountCode": "00",
                    "maxAmount": chem.get("Maximum Daily Amount Stored(pounds)", 0),
                    "maxAmountCode": "00",
                    "belowReportingThresholds": chem.get("Below Reporting Thresholds", False),
                    "confidentialStorageLocs": False,
                    "tradeSecret": False,
                    "daysOnSite": 365,
                    "sameAsLastYear": False,
                    "storageLocations": [{
                        "locationDescription": "DummyLocation",
                        "storageType": "DummyStorageType",
                        "pressure": "DummyPressure",
                        "temperature": "DummyTemperature",
                        "amount": 0,
                        "unit": "DummyUnit"
                    }],
                    "mixtureComponents": [{
                        "componentName": "DummyComponent",
                        "casNumber": "000-00-0",
                        "ehs": False,
                        "maxAmountCode": "00",
                        "componentPercentage": 0,
                        "weightOrVolume": "DummyWeightOrVolume"
                    }]
                }],
                "contacts": [{
                    "firstName": "DummyFirstName",
                    "lastName": "DummyLastName",
                    "title": "DummyTitle",
                    "email": "dummy@example.com",
                    "mailingAddress": {
                        "street": "DummyStreet",
                        "city": "DummyCity",
                        "state": "DummyState",
                        "zipcode": "00000",
                        "country": "DummyCountry"
                    },
                    "contactTypes": ["DummyContactType"],
                    "phones": [{
                        "phoneNumber": "000-000-0000",
                        "phoneType": "DummyType"
                    }],
                    "lastModified": "2000-01-01"
                }]
            }

            final_json["facilities"].append(facility)

    return final_json
