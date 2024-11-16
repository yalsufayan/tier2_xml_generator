from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import xml.etree.ElementTree as ET
from typing import List, Optional
import os
import zipfile
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from main import get_final_json
from firebase_admin import firestore  # Change this import to firestore


app = FastAPI()

# Initialize the app with your service account key
cred = credentials.Certificate('service.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://evotrack-ff16b-default-rtdb.firebaseio.com/'
})

# Reference to the Realtime Database
ref = db.reference('/')

# Define allowed origins
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://example.com"
]

# Reference to Firestore (Firestore, not Realtime Database)
db = firestore.client()

# Define allowed origins
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://example.com"
]

# Function to add data to Firestore
def add_document(collection_name, document_id, data):
    try:
        # Add document to Firestore
        db.collection(collection_name).document(document_id).set(data)
        print(f"Document '{document_id}' successfully written to '{collection_name}' collection.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specific origins
    allow_credentials=True,
    allow_methods=["*"],    # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],    # Allow all headers
)


# Define the Pydantic models for the data structure
class Address(BaseModel):
    street: str
    city: str
    state: str
    zipcode: str
    country: Optional[str] = "USA"

class LatLong(BaseModel):
    latitude: float
    longitude: float

class Phone(BaseModel):
    phoneNumber: str
    phoneType: str

class Hazard(BaseModel):
    category: str
    value: bool

class StorageLocation(BaseModel):
    locationDescription: str
    storageType: str
    pressure: str
    temperature: str
    amount: int
    unit: str

class MixtureComponent(BaseModel):
    componentName: str
    casNumber: Optional[str] = None
    ehs: bool
    maxAmountCode: Optional[str] = None
    componentPercentage: float
    weightOrVolume: str

class Chemical(BaseModel):
    chemName: str
    casNumber: str
    ehs: bool
    pure: bool
    mixture: bool
    solid: bool
    liquid: bool
    gas: bool
    hazards: List[Hazard]
    aveAmount: int
    aveAmountCode: str
    maxAmount: int
    maxAmountCode: str
    belowReportingThresholds: bool
    confidentialStorageLocs: bool
    tradeSecret: bool
    daysOnSite: int
    sameAsLastYear: bool
    storageLocations: List[StorageLocation]
    mixtureComponents: Optional[List[MixtureComponent]] = None

class StateField(BaseModel):
    label: str
    t2sFieldname: str
    data: Optional[str] = None

class FacilityId(BaseModel):
    recordid: str
    type: str
    id: str
    description: Optional[str] = None

class FacilityContact(BaseModel):
    firstName: Optional[str] = None
    lastName: str
    title: Optional[str] = None
    email: Optional[str] = None
    mailingAddress: Address
    contactTypes: List[str]
    phones: List[Phone]
    lastModified: str

class Facility(BaseModel):
    recordid: str
    facilityName: str
    streetAddress: Address
    mailingAddress: Address
    county: str
    fireDistrict: str
    latLong: LatLong
    department: str
    notes: str
    sitePlanAttached: bool
    siteCoordAbbrevAttached: bool
    dikeDescriptionAttached: bool
    facilityInfoSameAsLastYear: bool
    nameAndTitleOfCertifier: str
    dateSigned: str
    feesTotal: float
    phone: Phone
    manned: bool
    maxNumOccupants: Optional[int]
    subjectToChemAccidentPrevention: bool
    subjectToEmergencyPlanning: bool
    LEPC: Optional[str]
    contactIds: List[str]
    chemicals: List[Chemical]
    stateFields: Optional[List[StateField]]
    facilityIds: Optional[List[FacilityId]]
    lastModified: str
    contacts: List[FacilityContact]

class Dataset(BaseModel):
    reportyear: int
    facilities: List[Facility]

# Function to generate XML
def generate_xml(dataset: Dataset):
    root = ET.Element("epcraTier2Dataset", xmlns="https://cameo.noaa.gov/epcra_tier2/data_standard/v1", version="1.0.0")
    dataset_elem = ET.SubElement(root, "dataset", reportyear=str(dataset.reportyear))

    for facility in dataset.facilities:
        facility_elem = ET.SubElement(dataset_elem, "facility", recordid=facility.recordid)
        ET.SubElement(facility_elem, "facilityName").text = facility.facilityName

        # Add street and mailing addresses
        street_elem = ET.SubElement(facility_elem, "streetAddress")
        ET.SubElement(street_elem, "street").text = facility.streetAddress.street
        ET.SubElement(street_elem, "city").text = facility.streetAddress.city
        ET.SubElement(street_elem, "state").text = facility.streetAddress.state
        ET.SubElement(street_elem, "zipcode").text = facility.streetAddress.zipcode
        
        mailing_elem = ET.SubElement(facility_elem, "mailingAddress")
        ET.SubElement(mailing_elem, "street").text = facility.mailingAddress.street
        ET.SubElement(mailing_elem, "city").text = facility.mailingAddress.city
        ET.SubElement(mailing_elem, "state").text = facility.mailingAddress.state
        ET.SubElement(mailing_elem, "zipcode").text = facility.mailingAddress.zipcode
        ET.SubElement(mailing_elem, "country").text = facility.mailingAddress.country

        # Additional Facility Elements
        ET.SubElement(facility_elem, "county").text = facility.county
        ET.SubElement(facility_elem, "fireDistrict").text = facility.fireDistrict

        # LatLong
        latlong_elem = ET.SubElement(facility_elem, "latLong")
        ET.SubElement(latlong_elem, "latitude").text = str(facility.latLong.latitude)
        ET.SubElement(latlong_elem, "longitude").text = str(facility.latLong.longitude)

        # Contact details, certification info, etc.
        ET.SubElement(facility_elem, "department").text = facility.department
        ET.SubElement(facility_elem, "notes").text = facility.notes
        ET.SubElement(facility_elem, "sitePlanAttached").text = str(facility.sitePlanAttached).lower()
        ET.SubElement(facility_elem, "siteCoordAbbrevAttached").text = str(facility.siteCoordAbbrevAttached).lower()
        ET.SubElement(facility_elem, "dikeDescriptionAttached").text = str(facility.dikeDescriptionAttached).lower()
        ET.SubElement(facility_elem, "facilityInfoSameAsLastYear").text = str(facility.facilityInfoSameAsLastYear).lower()
        ET.SubElement(facility_elem, "nameAndTitleOfCertifier").text = facility.nameAndTitleOfCertifier
        ET.SubElement(facility_elem, "dateSigned").text = facility.dateSigned
        ET.SubElement(facility_elem, "feesTotal").text = str(facility.feesTotal)
        ET.SubElement(facility_elem, "LEPC").text = facility.LEPC or ""
        
        # Contact IDs
        contact_ids_elem = ET.SubElement(facility_elem, "contactIds")
        for contact_id in facility.contactIds:
            ET.SubElement(contact_ids_elem, "contactId").text = contact_id

        # Phone
        phone_elem = ET.SubElement(facility_elem, "phone", recordid=facility.phone.phoneNumber)
        ET.SubElement(phone_elem, "phoneNumber").text = facility.phone.phoneNumber
        ET.SubElement(phone_elem, "phoneType").text = facility.phone.phoneType

        # Other facility details
        ET.SubElement(facility_elem, "manned").text = str(facility.manned).lower()
        ET.SubElement(facility_elem, "maxNumOccupants").text = str(facility.maxNumOccupants) if facility.maxNumOccupants else ""
        ET.SubElement(facility_elem, "subjectToChemAccidentPrevention").text = str(facility.subjectToChemAccidentPrevention).lower()
        ET.SubElement(facility_elem, "subjectToEmergencyPlanning").text = str(facility.subjectToEmergencyPlanning).lower()

        # Facility IDs
        facility_ids_elem = ET.SubElement(facility_elem, "facilityIds")
        for fid in facility.facilityIds:
            fid_elem = ET.SubElement(facility_ids_elem, "facilityId", recordid=fid.recordid, type=fid.type)
            ET.SubElement(fid_elem, "id").text = fid.id
            if fid.description:
                ET.SubElement(fid_elem, "description").text = fid.description

        # State Fields
        state_fields_elem = ET.SubElement(facility_elem, "stateFields")
        for field in facility.stateFields or []:
            state_field_elem = ET.SubElement(state_fields_elem, "stateField", required="true" if field.data else "false")
            ET.SubElement(state_field_elem, "label").text = field.label
            ET.SubElement(state_field_elem, "t2sFieldname").text = field.t2sFieldname
            if field.data:
                ET.SubElement(state_field_elem, "data").text = field.data

        # Chemicals
        chemicals_elem = ET.SubElement(facility_elem, "chemicals")
        for chemical in facility.chemicals:
            chem_elem = ET.SubElement(chemicals_elem, "chemical", recordid=facility.recordid)
            ET.SubElement(chem_elem, "chemName").text = chemical.chemName
            ET.SubElement(chem_elem, "casNumber").text = chemical.casNumber
            ET.SubElement(chem_elem, "ehs").text = str(chemical.ehs).lower()
            ET.SubElement(chem_elem, "pure").text = str(chemical.pure).lower()
            ET.SubElement(chem_elem, "mixture").text = str(chemical.mixture).lower()
            ET.SubElement(chem_elem, "solid").text = str(chemical.solid).lower()
            ET.SubElement(chem_elem, "liquid").text = str(chemical.liquid).lower()
            ET.SubElement(chem_elem, "gas").text = str(chemical.gas).lower()

            # Hazards
            hazards_elem = ET.SubElement(chem_elem, "hazards")
            for hazard in chemical.hazards:
                hazard_elem = ET.SubElement(hazards_elem, "hazard")
                ET.SubElement(hazard_elem, "category").text = hazard.category
                ET.SubElement(hazard_elem, "value").text = str(hazard.value).lower()
            
            # Storage locations
            storage_locations_elem = ET.SubElement(chem_elem, "storageLocations")
            for location in chemical.storageLocations:
                location_elem = ET.SubElement(storage_locations_elem, "storageLocation", recordid=facility.recordid)
                ET.SubElement(location_elem, "locationDescription").text = location.locationDescription
                ET.SubElement(location_elem, "storageType").text = location.storageType
                ET.SubElement(location_elem, "pressure").text = location.pressure
                ET.SubElement(location_elem, "temperature").text = location.temperature
                ET.SubElement(location_elem, "amount").text = str(location.amount)
                ET.SubElement(location_elem, "unit").text = location.unit
            
            # Mixture components
            if chemical.mixtureComponents:
                mixture_components_elem = ET.SubElement(chem_elem, "mixtureComponents")
                for component in chemical.mixtureComponents:
                    component_elem = ET.SubElement(mixture_components_elem, "mixtureComponent")
                    ET.SubElement(component_elem, "componentName").text = component.componentName
                    ET.SubElement(component_elem, "casNumber").text = component.casNumber or ""
                    ET.SubElement(component_elem, "ehs").text = str(component.ehs).lower()
                    ET.SubElement(component_elem, "maxAmountCode").text = component.maxAmountCode or ""
                    ET.SubElement(component_elem, "componentPercentage").text = str(component.componentPercentage)
                    ET.SubElement(component_elem, "weightOrVolume").text = component.weightOrVolume

        # Contacts
        contacts_elem = ET.SubElement(facility_elem, "contacts")
        for contact in facility.contacts:
            contact_elem = ET.SubElement(contacts_elem, "contact", recordid=contact.lastModified)
            ET.SubElement(contact_elem, "firstName").text = contact.firstName or ""
            ET.SubElement(contact_elem, "lastName").text = contact.lastName
            ET.SubElement(contact_elem, "title").text = contact.title or ""
            ET.SubElement(contact_elem, "email").text = contact.email or ""

            mailing_address_elem = ET.SubElement(contact_elem, "mailingAddress")
            ET.SubElement(mailing_address_elem, "street").text = contact.mailingAddress.street
            ET.SubElement(mailing_address_elem, "city").text = contact.mailingAddress.city
            ET.SubElement(mailing_address_elem, "state").text = contact.mailingAddress.state
            ET.SubElement(mailing_address_elem, "zipcode").text = contact.mailingAddress.zipcode
            ET.SubElement(mailing_address_elem, "country").text = contact.mailingAddress.country

            contact_types_elem = ET.SubElement(contact_elem, "contactTypes")
            for ctype in contact.contactTypes:
                ET.SubElement(contact_types_elem, "contactType").text = ctype

            phones_elem = ET.SubElement(contact_elem, "phones")
            for phone in contact.phones:
                phone_elem = ET.SubElement(phones_elem, "phone")
                ET.SubElement(phone_elem, "phoneNumber").text = phone.phoneNumber
                ET.SubElement(phone_elem, "phoneType").text = phone.phoneType

            ET.SubElement(contact_elem, "lastModified").text = contact.lastModified

    # Write XML to file
    tree = ET.ElementTree(root)
    tree.write("./output.xml", encoding="utf-8", xml_declaration=True)
    return ET.tostring(root, encoding='utf-8', method='xml').decode()

@app.post("/generate_xml")
def create_xml(dataset: Dataset):
    try:
        xml_data = generate_xml(dataset)
        with zipfile.ZipFile("Tier2Report.zip", 'w') as zip_file:
            zip_file.write("output.xml")
        
        # collection = "users"
        # doc_id = "reports"
        # user_data = {
        # "xml": xml_data
        # }
        # add_document(collection, doc_id, user_data)

        ref.set({
            'xml': xml_data
        })
        return {"xml": xml_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add an endpoint to fetch data from main.py and generate XML
@app.get("/generate_xml_from_main")
def generate_xml_from_main():
    try:
        # Get JSON from main.py
        dataset_json = get_final_json()
        
        # Use the dataset to generate XML
        xml_data = generate_xml(Dataset(**dataset_json))  # Parse JSON into Dataset model

        # Save to Firestore
        data = {
            "xmlData": xml_data,
            "reportYear": dataset.reportyear
        }
        add_document("tier2_reports", str(dataset.reportyear), data)
        return {"message": "XML generated and saved to Firestore successfully!"}
        
        # Save XML to a file and return
        with open("output_from_main.xml", "w") as file:
            file.write(xml_data)
        
        return {"message": "XML generated successfully", "xml": xml_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(TEMP_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path, filename=filename, media_type='application/zip')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)