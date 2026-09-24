import os
import random
from datetime import datetime, timedelta

import pandas as pd
import requests
#from dotenv import load_dotenv
import streamlit as st 

# =========================================================
# ENVIRONMENT / API CONFIGURATION
# =========================================================

#load_dotenv()

rapidapi_key = st.secrets["RAPIDAPI_KEY"]#os.getenv("RAPIDAPI_KEY")
openrouter_key = st.secret["OPENROUTER_API_KEY"]#os.getenv("OPENROUTER_API_KEY")

llm_url = "https://openrouter.ai/api/v1/chat/completions"

llm_headers = {
    "Authorization": f"Bearer {openrouter_key}",
    "Content-Type": "application/json"
}


# =========================================================
# MEDICATION DATA STRUCTURE
# =========================================================

medication_columns = [
    "medication_id",
    "medication_name",
    "ingredients_substances",
    "symptoms_tags",
    "dosage_frequency_value",
    "dosage_frequency_unit",
    "usage_safety_instructions",
    "urgency_level",
    "medication_type",
    "dose_quantity",
    "dose_unit",
    "start_time",
    "current_supply",
    "refill_threshold",
    "expiration_date",
    "compliance_rating",
    "api_generic_name",
    "api_substances"
]


# =========================================================
# EXTERNAL MEDICATION API
# =========================================================

def search_medication_api(medication_name):
    """
    Search the external medication API using a medication name.

    Parameters:
        medication_name (str): Medication name entered by the user.

    Returns:
        list: Medication records returned by the API.
    """

    url = (
        "https://drug-information-api-fda-labels-and-ndc-lookup."
        "p.rapidapi.com/drugs/search"
    )

    querystring = {
        "limit": "10",
        "q": medication_name
    }

    headers = {
        "x-rapidapi-key": rapidapi_key,
        "x-rapidapi-host":
            "drug-information-api-fda-labels-and-ndc-lookup.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    response = requests.get(
        url,
        headers=headers,
        params=querystring
    )

    if response.status_code == 200:
        return response.json()

    return []


def process_api_results(api_results):
    """
    Convert raw RapidAPI medication results into cleaner records.

    Parameters:
        api_results (list): Raw medication records from RapidAPI.

    Returns:
        list: Cleaned medication records.
    """

    cleaned_results = []

    for medication in api_results:

        substances = medication.get("substance_name", [])

        if isinstance(substances, list):
            substances = ", ".join(substances)

        cleaned_medication = {
            "brand_name": medication.get("brand_name", "Unknown"),
            "generic_name": medication.get("generic_name", "Unknown"),
            "substances": substances,
            "route": medication.get("route", []),
            "dosage_form": medication.get("dosage_form", "Unknown"),
            "purpose": medication.get("purpose", "Not available"),
            "warnings": medication.get("warnings", "Not available"),
            "indications_and_usage": medication.get(
                "indications_and_usage",
                "Not available"
            )
        }

        cleaned_results.append(cleaned_medication)

    return cleaned_results


# =========================================================
# WELLNESS / MEDICATION SPOTLIGHT
# =========================================================

def get_random_wellness_spotlight():
    """
    Generate a random wellness tip or medication spotlight
    using the OpenRouter API.

    Returns:
        dict: Type and generated content.
    """

    spotlight_type = random.choice(
        ["Wellness Tip", "Medication Spotlight"]
    )

    prompt = f"""
Generate one short {spotlight_type} for a medication tracking application.

Rules:
- Keep it simple and useful.
- Maximum 2 sentences.
- Do not diagnose medical conditions.
- Do not recommend changing medication doses.
- Do not tell users to start or stop prescription medication.
- Do not provide personalized medical advice.
- Return only the {spotlight_type}, with no heading.
"""

    payload = {
        "model": "openrouter/free",
        "temperature": 1.0,
        "messages": [
            {
                "role": "system",
                "content": """
You are MediTrack's wellness and medication information assistant.
Provide safe, clear, general health and medication education.
Do not diagnose, prescribe, or change a user's treatment.
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        response = requests.post(
            llm_url,
            headers=llm_headers,
            json=payload
        )

        if response.status_code == 200:
            data = response.json()

            content = (
                data["choices"][0]["message"]["content"]
                .strip()
            )

            return {
                "type": spotlight_type,
                "content": content
            }

        return {
            "type": "Wellness Tip",
            "content":
                "Stay hydrated and follow your medication instructions carefully."
        }

    except (
        requests.RequestException,
        KeyError,
        IndexError,
        TypeError
    ):
        return {
            "type": "Wellness Tip",
            "content":
                "Stay hydrated and follow your medication instructions carefully."
        }


# =========================================================
# CSV LOAD / SAVE
# =========================================================

def load_medications():
    """
    Load saved medication records from medications.csv.

    Returns:
        DataFrame: Saved medication records.
    """

    if os.path.exists("medications.csv"):
        return pd.read_csv("medications.csv")

    return pd.DataFrame(columns=medication_columns)


def save_medications(medications_df):
    """
    Save medication records to medications.csv.

    Parameters:
        medications_df (DataFrame): Medication records to save.
    """

    medications_df.to_csv(
        "medications.csv",
        index=False
    )


# =========================================================
# DUPLICATE CHECK
# =========================================================

def is_duplicate_medication(medications_df, medication_name):
    """
    Check whether a medication is already saved.

    Returns:
        bool: True if medication exists, otherwise False.
    """

    medication_name = medication_name.strip().lower()

    if medications_df.empty:
        return False

    saved_names = (
        medications_df["medication_name"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    return medication_name in saved_names.values


# =========================================================
# ADD MEDICATION
# =========================================================

def add_medication(
    medications_df,
    medication_name,
    ingredients_substances,
    dosage_frequency_value,
    dosage_frequency_unit,
    usage_safety_instructions,
    urgency_level,
    symptoms_tags="",
    start_time="",
    current_supply="",
    refill_threshold="",
    expiration_date=""
):
    """
    Add a new medication record to the tracker.

    Returns:
        DataFrame: Updated medication records.
    """

    if is_duplicate_medication(
        medications_df,
        medication_name
    ):
        return medications_df

    if medications_df.empty:
        medication_id = 1
    else:
        medication_id = (
            medications_df["medication_id"].max() + 1
        )

    new_medication = {
        "medication_id": medication_id,
        "medication_name": medication_name,
        "ingredients_substances": ingredients_substances,
        "symptoms_tags": symptoms_tags,
        "dosage_frequency_value": dosage_frequency_value,
        "dosage_frequency_unit": dosage_frequency_unit,
        "usage_safety_instructions": usage_safety_instructions,
        "urgency_level": urgency_level,
        "medication_type": "",
        "dose_quantity": "",
        "dose_unit": "",
        "start_time": start_time,
        "current_supply": current_supply,
        "refill_threshold": refill_threshold,
        "expiration_date": expiration_date,
        "compliance_rating": "",
        "api_generic_name": "",
        "api_substances": ""
    }

    medications_df.loc[len(medications_df)] = new_medication

    save_medications(medications_df)

    return medications_df


# =========================================================
# SEARCH SAVED MEDICATIONS
# =========================================================

def search_saved_medications(
    medications_df,
    search_text
):
    """
    Search saved medications by medication name,
    ingredient/substance, or symptom tag.

    Returns:
        DataFrame: Matching medication records.
    """

    search_text = search_text.strip().lower()

    if search_text == "":
        return pd.DataFrame(
            columns=medications_df.columns
        )

    name_match = (
        medications_df["medication_name"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.contains(search_text, regex=False)
    )

    ingredient_match = (
        medications_df["ingredients_substances"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.contains(search_text, regex=False)
    )

    symptom_match = (
        medications_df["symptoms_tags"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.contains(search_text, regex=False)
    )

    matches = medications_df[
        name_match |
        ingredient_match |
        symptom_match
    ]

    return matches


# =========================================================
# SHARED INGREDIENT RISK
# =========================================================

def check_shared_ingredient_risk(
    medications_df,
    search_text
):
    """
    Find saved medications containing the same
    searched ingredient.

    Returns:
        list: Matching medication names.
    """

    search_text = search_text.strip().lower()

    if search_text == "":
        return []

    ingredient_match = (
        medications_df["ingredients_substances"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.contains(search_text, regex=False)
    )

    matching_medications = medications_df.loc[
        ingredient_match,
        "medication_name"
    ].tolist()

    return matching_medications


# =========================================================
# NEXT INTAKE
# =========================================================

def calculate_next_intake(
    start_time,
    frequency_value,
    frequency_unit
):
    """
    Calculate the next scheduled medication intake time.

    Returns:
        datetime or None.
    """

    if (
        pd.isna(start_time)
        or str(start_time).strip() == ""
    ):
        return None

    try:
        start = datetime.strptime(
            str(start_time),
            "%H:%M"
        ).replace(
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day
        )

        frequency_value = int(frequency_value)

        if (
            str(frequency_unit)
            .lower()
            .startswith("hour")
        ):
            interval = timedelta(
                hours=frequency_value
            )
        else:
            interval = timedelta(
                minutes=frequency_value
            )

        next_time = start

        while next_time <= datetime.now():
            next_time += interval

        return next_time

    except (ValueError, TypeError):
        return None


# =========================================================
# DAILY 24-HOUR SCHEDULE
# =========================================================

def generate_daily_schedule(medications_df):
    """
    Generate a chronological medication schedule
    for a 24-hour day.

    Returns:
        list: Medication names and scheduled times.
    """

    schedule = []

    today = datetime.now().date()

    for _, medication in medications_df.iterrows():

        start_time = medication["start_time"]

        if (
            pd.isna(start_time)
            or str(start_time).strip() == ""
        ):
            continue

        try:
            first_dose = datetime.strptime(
                str(start_time),
                "%H:%M"
            )

            current_dose = datetime.combine(
                today,
                first_dose.time()
            )

            frequency_value = int(
                medication[
                    "dosage_frequency_value"
                ]
            )

            if frequency_value <= 0:
                continue

            frequency_unit = str(
                medication[
                    "dosage_frequency_unit"
                ]
            ).lower()

            if frequency_unit.startswith("hour"):
                interval = timedelta(
                    hours=frequency_value
                )
            else:
                interval = timedelta(
                    minutes=frequency_value
                )

            end_of_day = datetime.combine(
                today + timedelta(days=1),
                datetime.min.time()
            )

            while current_dose < end_of_day:

                schedule.append({
                    "medication_name":
                        medication["medication_name"],
                    "time": current_dose
                })

                current_dose += interval

        except (ValueError, TypeError):
            continue

    schedule.sort(
        key=lambda item: item["time"]
    )

    return schedule


# =========================================================
# EXPIRATION CHECK
# =========================================================

def check_expiration_status(
    expiration_date,
    warning_days=7
):
    """
    Check whether medication is expired,
    expiring soon, or okay.

    Returns:
        str: Expired, Expiring Soon, OK, or Unknown.
    """

    if (
        pd.isna(expiration_date)
        or str(expiration_date).strip() == ""
    ):
        return "Unknown"

    try:
        expiration = (
            pd.to_datetime(expiration_date)
            .date()
        )

        today = datetime.now().date()

        days_remaining = (
            expiration - today
        ).days

        if days_remaining < 0:
            return "Expired"

        elif days_remaining <= warning_days:
            return "Expiring Soon"

        else:
            return "OK"

    except (ValueError, TypeError):
        return "Unknown"


# =========================================================
# LOW SUPPLY CHECK
# =========================================================

def check_low_supply(
    current_supply,
    refill_threshold
):
    """
    Check whether medication supply is low.

    Returns:
        bool: True when refill warning is needed.
    """

    try:
        return (
            float(current_supply)
            <= float(refill_threshold)
        )

    except (ValueError, TypeError):
        return False


# =========================================================
# DELETE MEDICATIONS
# =========================================================

def delete_medications(
    medications_df,
    medication_ids=None,
    delete_all=False
):
    """
    Delete one, multiple, or all medications.

    Returns:
        DataFrame: Updated medication records.
    """

    if delete_all:
        return medications_df.iloc[0:0].copy()

    if medication_ids:
        updated_df = medications_df[
            ~medications_df[
                "medication_id"
            ].isin(medication_ids)
        ].copy()

        return updated_df

    return medications_df.copy()
