💊 MediTrack



MediTrack is a Streamlit-based Digital Medication Tracker \& Personal Health Record that helps users organize medications, track schedules, monitor medication supply and expiration, calculate refill requirements, record medication intake history, and search medication information using an external drug API.



The project was developed as a Python course project using Python, Pandas, Streamlit, CSV-based storage, RapidAPI, and OpenRouter.



🌐 Live App



Streamlit App:

https://meditrack-first-project-mvp.streamlit.app



🎥 Video Demo



Project Demo Video:

ADD YOUR VIDEO LINK HERE



✨ Main Features

Medication Management



Users can add medications with:



Medication name

Active ingredients / interacting substances

Symptoms / tags

Medication type

Dose quantity

Dose unit

Dosage frequency

Usage and safety instructions

Urgency level

First dose / start time

Current supply

Refill threshold

Expiration date

Self-reported compliance rating



The application prevents duplicate medication entries and allows users to delete selected medications or all medications.



Medication Categories



Medications can be categorized as:



Prescription

Over-the-Counter (OTC)

Supplement

First Aid

Medication Search



Users can search saved medications by:



Medication name

Active ingredient / substance

Symptom / tag



The application can also identify potential shared-ingredient overlap between saved medications.



MediTrack also integrates with an external medication database through RapidAPI.



Medication Schedule



MediTrack can:



Calculate the next scheduled medication intake

Generate a chronological 24-hour medication schedule

Display dose quantity and dose unit for scheduled medications

Medication Alerts



The application detects:



Expired medications

Medications expiring soon

Low medication supply



Warnings are displayed directly in the Streamlit interface.



Custom Medication Quantity Calculator



Users can select a medication and calculate the amount required for a custom number of days.



Example:



1 tablet every 8 hours for 30 days

= 90 tablets required



Compliance Rating



Users can assign a self-reported medication compliance rating from 1 to 5 stars.



The medication list can also be sorted from the highest compliance rating to the lowest.



Pharmacy Refill Request List



Users can:



Select multiple medications

Choose the required number of refill days

Generate a consolidated pharmacy refill request



The refill request displays:



Medication name

Ingredients / substances

Medication type

Dose quantity

Dose unit

Required quantity

Current supply

Refill quantity

Refill status



The refill calculation considers the medication already available in the user's current supply.



Medication Intake History



MediTrack stores medication intake activity in a separate intake\_history.csv file.



Each intake record contains:



Intake ID

Medication ID

Medication name

Scheduled time

Status

Recorded time



Users can record a scheduled medication dose as:



Taken

Missed



The application prevents duplicate history records for the same medication and scheduled dose.



Daily Dose Tracking



Scheduled medication doses can have the following statuses:



Upcoming

Due

Overdue

Taken

Missed



A default 60-minute grace period is used before an unrecorded scheduled dose becomes Overdue.



The application also displays alerts for overdue doses that have not been recorded.



Wellness \& Medication Spotlight



MediTrack uses OpenRouter to generate:



General wellness tips

Medication information spotlights



The generated content is intended for general educational purposes and is not a replacement for professional medical advice.



🛠️ Technologies Used

Python

Streamlit

Pandas

Requests

CSV files

RapidAPI

OpenRouter API



Python standard-library modules used include:



os

random

math

datetime

📂 Project Structure



MediTrack/



app.py

myutils.py

medications.csv

intake\_history.csv

requirements.txt

.gitignore

README.md



app.py



Contains the Streamlit user interface and connects user actions to the functions inside myutils.py.



myutils.py



Contains reusable application logic including:



CSV loading and saving

Medication creation

Duplicate medication checking

Saved medication search

External medication API requests

Wellness spotlight generation

Medication quantity calculations

Compliance sorting

Pharmacy refill calculations

Next intake calculations

Daily schedule generation

Expiration checks

Low-supply checks

Intake-history logging

Daily dose status calculation

Overdue-dose alerts

Medication deletion

medications.csv



Stores saved medication records.



intake\_history.csv



Stores repeated medication intake events such as Taken and Missed doses.



🔐 API Keys and Secrets



API keys are not stored directly inside the source code.



MediTrack uses Streamlit Secrets for:



RAPIDAPI\_KEY

OPENROUTER\_API\_KEY



For local development, the keys can be stored inside:



.streamlit/secrets.toml



The secrets file is excluded from GitHub using .gitignore.



▶️ Running the Project Locally

Step 1: Clone the repository



git clone YOUR\_REPOSITORY\_URL



Step 2: Open the project directory



cd MediTrack



Step 3: Install the required packages



pip install -r requirements.txt



Step 4: Create the Streamlit secrets file



Create:



.streamlit/secrets.toml



Add:



RAPIDAPI\_KEY = "your\_rapidapi\_key"



OPENROUTER\_API\_KEY = "your\_openrouter\_key"



Step 5: Run the Streamlit application



python -m streamlit run app.py



🧪 Example Test Medication



Medication Name: Panadol Test



Active Ingredient: Paracetamol



Symptoms / Tags: headache, pain



Medication Type: Over-the-Counter (OTC)



Dose Quantity: 1



Dose Unit: Tablet



Dosage Frequency: 24 Hours



Urgency Level: Low



Compliance Rating: 5 stars



Current Supply: 5



Refill Threshold: 2



Expiration Date: Future date



For a 30-day supply:



Required Quantity = 30 tablets



Current Supply = 5 tablets



Refill Quantity = 25 tablets



✅ Project Features Implemented

Medication management

Duplicate medication protection

Medication categories

Medication search

Search by ingredient and symptom

Shared-ingredient warning

Next intake calculation

24-hour medication schedule

Expiration alerts

Low-supply alerts

External medication API search

Wellness and medication spotlight

Custom medication quantity calculation

1–5 compliance rating

Compliance sorting

Pharmacy refill request list

Multi-medication refill selection

Refill quantity calculation

Intake-history tracking

Taken medication recording

Missed medication recording

Timestamped intake records

Upcoming dose status

Due dose status

Overdue dose status

Dynamic unrecorded-dose alerts

Delete selected medications

Delete all medications

⚠️ Important Notes



MediTrack is an educational project and is not a substitute for professional medical advice.



Medication information returned by external APIs should be treated as informational only.



The current MVP uses CSV files for data storage.



Because Streamlit Community Cloud uses temporary application storage, CSV data may reset when the deployed application restarts or is redeployed.



🚀 Possible Future Improvements



Future versions of MediTrack could include:



User accounts and authentication

Persistent cloud database storage

Edit medication functionality

Push notifications and reminders

Automatic medication supply reduction after recording a dose as Taken

Downloadable pharmacy refill reports

Medication compliance analytics

Dashboard charts

Mobile notifications

👨‍💻 Author



Abdulla Alhayki



Python / Data Science Project / project One





