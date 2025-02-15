import requests
import json

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
    """
    Fetches data from the API for the specified data type with pagination handling.
    """
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

def get_final_json(filter_id):
    """
    Generates the final JSON structure by combining business and chemical inventory data.
    """
    business_data = fetch_data(DATA_TYPES["Business"])
    # print("this is business\n",business_data)
    chemical_inventory_data = fetch_data(DATA_TYPES["Chemical Inventory"])
    # print("this is chemical data \n", chemical_inventory_data)
    business_dict = {biz["_id"]: biz for biz in business_data}

    final_json = {"reportYear": 2019, "facilities": []}

    for chem in chemical_inventory_data:
        business_id = chem.get("business")
        if business_id in business_dict:
            business = business_dict[business_id]

            # Filter by email if specified
            if filter_id and business.get("Created By") != filter_id:
                continue

            # Construct the facility structure
            facility = {
                "recordId": chem.get("_id", "DummyRecordID"),
                "facilityName": business.get("name", "Unknown Facility"),
                "streetAddress": {
                    "street": business.get("street", "Unknown Street"),
                    "city": business.get("city", "Unknown City"),
                    "state": business.get("state", "Unknown State"),
                    "zipcode": business.get("zip", "00000")
                },
                "mailingAddress": {
                    "street": business.get("street"),
                    "city": business.get("city"),
                    "state": business.get("state"),
                    "zipcode": business.get("zip"),
                    "country": business.get("country", "Unknown Country")
                },
                "county": business.get("country", ""),
                "fireDistrict": business.get("FireDistrict", "Unknown FireDistrict"),
                "latLong": {
                    "latitude": business.get("latitude", 0.0),
                    "longitude": business.get("longitude", 0.0)
                },
                "sitePlanAttached": business.get("site plan attached", False),
                "siteCoordAbbrevAttached": business.get("site coordinate abbreviation", False),
                "facilityInfoSameAsLastYear": business.get("info_same_as_last_year", False),
                "phone": {
                    "phoneNumber": business.get("phone", "000-000-0000"),
                    "phoneType": business.get("phoneType", "Unknown")
                },
                "manned": business.get("manned", False),
                "maxNumOccupants": business.get("max no. of occupants", 0),
                "subjectToChemAccidentPrevention": business.get("subject to chemical prevention", False),
                "subjectToEmergencyPlanning": business.get("emergency planning", False),
                "lastModified": business.get("last modified", "2000-01-01"),
                "chemicals": [{
                    "chemName": chem.get("Product Name", "Unknown Chemical"),
                    "casNumber": chem.get("Product Code/CAS", "000-00-0"),
                    "ehs": chem.get("is it EHS (extremely hazardous)?", False),
                    "pure": chem.get("Pure or Mixt.", "") == "Pure",
                    "mixture": chem.get("Pure or Mixt.", "") == "Mixture",
                    "solid": chem.get("Solid", False),
                    "liquid": chem.get("Liquid", False),
                    "gas": chem.get("Gas", False),
                    "aveAmount": chem.get("Average Daily Amount Stored(pounds)", 0),
                    "maxAmount": chem.get("Maximum Daily Amount Stored(pounds)", 0),
                    "belowReportingThresholds": chem.get("Below Reporting Thresholds", False),
                }],
                "contacts": [{
                    "firstName": business.get("Emergency fname"),
                    "lastName": business.get("Emergency lname"),
                    "email": business.get("emergency email 1"),
                    "mailingAddress": business.get("emergency mail address"),
                    "contactTypes": [business.get("emergency phone type")],
                    "phones": [{
                        "phoneNumber": business.get("emergency phone number 1"),
                        "phoneType": business.get("emergency phone type")
                    }],
                    "lastModified": business.get("Modified Date")
                }]
            }

            final_json["facilities"].append(facility)

    return final_json

def pretty_print_json(data):
    """
    Formats and prints JSON in a readable way.
    """
    try:
        formatted_json = json.dumps(data, indent=4)
        print(formatted_json)
        return formatted_json
    except (TypeError, ValueError) as e:
        print(f"Error formatting JSON: {e}")
        return None

# Fetch and print the final JSON
# final_data = get_final_json()
# pretty_print_json(final_data)
