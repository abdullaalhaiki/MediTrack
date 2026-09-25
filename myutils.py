import os
import random
from datetime import datetime, timedelta

import pandas as pd
import requests
#from dotenv import load_dotenv
import streamlit as st 
import math
# =========================================================
# ENVIRONMENT / API CONFIGURATION
# =========================================================

#load_dotenv()

rapidapi_key = st.secrets["RAPIDAPI_KEY"]#os.getenv("RAPIDAPI_KEY")
openrouter_key = st.secrets["OPENROUTER_API_KEY"]#os.getenv("OPENROUTER_API_KEY")

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
# INTAKE HISTORY DATA STRUCTURE
# =========================================================

INTAKE_HISTORY_FILE = "intake_history.csv"

intake_history_columns = [
    "intake_id",
    "medication_id",
    "medication_name",
    "scheduled_time",
    "status",
    "recorded_time"
]


# =========================================================
# EXTERNAL MEDICATION API
# =========================================================

def search_medication_api(medication_name):
    """
    Search the external medication API using a medication name.

    Parameters:
        medication_name (str):
        Medication name entered by the user.

    Returns:
        list:
        Medication records returned by the API.
    """

    medication_name = str(
        medication_name
    ).strip()

    if medication_name == "":
        return []

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

    try:

        response = requests.get(
            url,
            headers=headers,
            params=querystring,
            timeout=15
        )

        if response.status_code == 200:

            data = response.json()

            if isinstance(data, list):
                return data

        return []

    except (
        requests.RequestException,
        ValueError,
        TypeError
    ):

        return []


def process_api_results(api_results):
    """
    Convert raw RapidAPI medication results
    into cleaner records.

    Parameters:
        api_results (list):
        Raw medication records from RapidAPI.

    Returns:
        list:
        Cleaned medication records.
    """

    if not isinstance(
        api_results,
        list
    ):
        return []

    cleaned_results = []

    for medication in api_results:

        if not isinstance(
            medication,
            dict
        ):
            continue

        substances = medication.get(
            "substance_name",
            []
        )

        if isinstance(
            substances,
            list
        ):
            substances = ", ".join(
                substances
            )

        elif substances is None:
            substances = ""

        else:
            substances = str(
                substances
            )

        cleaned_medication = {

            "brand_name":
                medication.get(
                    "brand_name",
                    "Unknown"
                ),

            "generic_name":
                medication.get(
                    "generic_name",
                    "Unknown"
                ),

            "substances":
                substances,

            "route":
                medication.get(
                    "route",
                    []
                ),

            "dosage_form":
                medication.get(
                    "dosage_form",
                    "Unknown"
                ),

            "purpose":
                medication.get(
                    "purpose",
                    "Not available"
                ),

            "warnings":
                medication.get(
                    "warnings",
                    "Not available"
                ),

            "indications_and_usage":
                medication.get(
                    "indications_and_usage",
                    "Not available"
                )
        }

        cleaned_results.append(
            cleaned_medication
        )

    return cleaned_results


# =========================================================
# WELLNESS / MEDICATION SPOTLIGHT
# =========================================================

def get_random_wellness_spotlight():
    """
    Generate a random wellness tip
    or medication spotlight using OpenRouter.

    Returns:
        dict:
        Type and generated content.
    """

    spotlight_type = random.choice(
        [
            "Wellness Tip",
            "Medication Spotlight"
        ]
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
            json=payload,
            timeout=30
        )

        if response.status_code == 200:

            data = response.json()

            content = (
                data[
                    "choices"
                ][0][
                    "message"
                ][
                    "content"
                ]
                .strip()
            )

            if content:

                return {
                    "type":
                        spotlight_type,

                    "content":
                        content
                }

        return {
            "type":
                "Wellness Tip",

            "content":
                "Stay hydrated and follow your medication instructions carefully."
        }

    except (
        requests.RequestException,
        KeyError,
        IndexError,
        TypeError,
        ValueError
    ):

        return {
            "type":
                "Wellness Tip",

            "content":
                "Stay hydrated and follow your medication instructions carefully."
        }


# =========================================================
# MEDICATION CSV LOAD / SAVE
# =========================================================

def load_medications():
    """
    Load saved medication records.

    If an older CSV is missing newer columns,
    add them automatically.

    Returns:
        DataFrame:
        Saved medication records.
    """

    if not os.path.exists(
        "medications.csv"
    ):

        return pd.DataFrame(
            columns=medication_columns
        )

    try:

        medications_df = pd.read_csv(
            "medications.csv"
        )

    except (
        pd.errors.EmptyDataError,
        FileNotFoundError
    ):

        return pd.DataFrame(
            columns=medication_columns
        )


    for column in medication_columns:

        if column not in medications_df.columns:

            medications_df[
                column
            ] = ""


    medications_df = medications_df[
        medication_columns
    ]


    return medications_df


def save_medications(
    medications_df
):
    """
    Save medication records to medications.csv.
    """

    medications_df = (
        medications_df.copy()
    )


    for column in medication_columns:

        if column not in medications_df.columns:

            medications_df[
                column
            ] = ""


    medications_df[
        medication_columns
    ].to_csv(
        "medications.csv",
        index=False
    )


# =========================================================
# INTAKE HISTORY CSV LOAD / SAVE
# =========================================================

def load_intake_history():
    """
    Load medication intake history.

    Returns:
        DataFrame:
        Existing intake history records.
    """

    if not os.path.exists(
        INTAKE_HISTORY_FILE
    ):

        return pd.DataFrame(
            columns=intake_history_columns
        )

    try:

        history_df = pd.read_csv(
            INTAKE_HISTORY_FILE
        )

    except (
        pd.errors.EmptyDataError,
        FileNotFoundError
    ):

        return pd.DataFrame(
            columns=intake_history_columns
        )


    for column in intake_history_columns:

        if column not in history_df.columns:

            history_df[
                column
            ] = ""


    return history_df[
        intake_history_columns
    ]


def save_intake_history(
    history_df
):
    """
    Save intake history to intake_history.csv.
    """

    history_df = history_df.copy()


    for column in intake_history_columns:

        if column not in history_df.columns:

            history_df[
                column
            ] = ""


    history_df[
        intake_history_columns
    ].to_csv(
        INTAKE_HISTORY_FILE,
        index=False
    )


# =========================================================
# DUPLICATE MEDICATION CHECK
# =========================================================

def is_duplicate_medication(
    medications_df,
    medication_name
):
    """
    Check whether a medication is already saved.

    Returns:
        bool:
        True if medication already exists.
    """

    medication_name = str(
        medication_name
    ).strip().lower()


    if medication_name == "":
        return False


    if medications_df.empty:
        return False


    saved_names = (
        medications_df[
            "medication_name"
        ]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )


    return (
        medication_name
        in saved_names.values
    )


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
    medication_type="",
    dose_quantity="",
    dose_unit="",
    start_time="",
    current_supply="",
    refill_threshold="",
    expiration_date="",
    compliance_rating=""
):
    """
    Add a new medication record.

    Returns:
        DataFrame:
        Updated medication records.
    """

    medication_name = str(
        medication_name
    ).strip()

    ingredients_substances = str(
        ingredients_substances
    ).strip()


    if medication_name == "":
        return medications_df


    if ingredients_substances == "":
        return medications_df


    if is_duplicate_medication(
        medications_df,
        medication_name
    ):

        return medications_df


    # Validate medication type.
    allowed_types = [
        "Prescription",
        "Over-the-Counter (OTC)",
        "Supplement",
        "First Aid"
    ]

    if (
        medication_type
        not in allowed_types
    ):

        medication_type = ""


    # Validate compliance rating.
    try:

        compliance_rating = int(
            compliance_rating
        )

        if compliance_rating not in [
            1, 2, 3, 4, 5
        ]:

            compliance_rating = ""

    except (
        ValueError,
        TypeError
    ):

        compliance_rating = ""


    # Safely create the next medication ID.
    if medications_df.empty:

        medication_id = 1

    else:

        existing_ids = pd.to_numeric(
            medications_df[
                "medication_id"
            ],
            errors="coerce"
        )

        max_id = existing_ids.max()

        if pd.isna(
            max_id
        ):

            medication_id = 1

        else:

            medication_id = (
                int(max_id)
                + 1
            )


    new_medication = {

        "medication_id":
            medication_id,

        "medication_name":
            medication_name,

        "ingredients_substances":
            ingredients_substances,

        "symptoms_tags":
            symptoms_tags,

        "dosage_frequency_value":
            dosage_frequency_value,

        "dosage_frequency_unit":
            dosage_frequency_unit,

        "usage_safety_instructions":
            usage_safety_instructions,

        "urgency_level":
            urgency_level,

        "medication_type":
            medication_type,

        "dose_quantity":
            dose_quantity,

        "dose_unit":
            dose_unit,

        "start_time":
            start_time,

        "current_supply":
            current_supply,

        "refill_threshold":
            refill_threshold,

        "expiration_date":
            expiration_date,

        "compliance_rating":
            compliance_rating,

        "api_generic_name":
            "",

        "api_substances":
            ""
    }


    medications_df.loc[
        len(
            medications_df
        )
    ] = new_medication


    save_medications(
        medications_df
    )


    return medications_df


# =========================================================
# REQUIRED QUANTITY CALCULATION
# =========================================================

def calculate_required_quantity(
    dose_quantity,
    frequency_value,
    frequency_unit,
    number_of_days
):
    """
    Calculate medication quantity needed
    for a custom number of days.

    Example:
        1 tablet every 8 hours for 30 days
        = 90 tablets.

    Returns:
        float:
        Total required quantity.
    """

    try:

        dose_quantity = float(
            dose_quantity
        )

        frequency_value = float(
            frequency_value
        )

        number_of_days = int(
            number_of_days
        )


        if (
            dose_quantity <= 0
            or frequency_value <= 0
            or number_of_days <= 0
        ):

            return 0


        frequency_unit = str(
            frequency_unit
        ).strip().lower()


        if frequency_unit.startswith(
            "hour"
        ):

            interval_minutes = (
                frequency_value
                * 60
            )


        elif frequency_unit.startswith(
            "minute"
        ):

            interval_minutes = (
                frequency_value
            )


        else:

            return 0


        total_minutes = (
            number_of_days
            * 24
            * 60
        )


        total_doses = math.ceil(
            total_minutes
            / interval_minutes
        )


        required_quantity = (
            total_doses
            * dose_quantity
        )


        return required_quantity


    except (
        ValueError,
        TypeError
    ):

        return 0


# =========================================================
# COMPLIANCE SORTING
# =========================================================

def sort_medications_by_compliance(
    medications_df
):
    """
    Sort medications from highest
    compliance rating to lowest.

    Blank ratings are placed last.
    """

    if medications_df.empty:

        return medications_df.copy()


    sorted_df = (
        medications_df.copy()
    )


    sorted_df[
        "compliance_rating"
    ] = pd.to_numeric(
        sorted_df[
            "compliance_rating"
        ],
        errors="coerce"
    )


    sorted_df = (
        sorted_df.sort_values(
            by="compliance_rating",
            ascending=False,
            na_position="last"
        )
    )


    return sorted_df


# =========================================================
# PHARMACY REFILL REQUEST LIST
# =========================================================

def generate_pharmacy_refill_list(
    medications_df,
    selected_medication_ids,
    number_of_days
):
    """
    Generate a consolidated pharmacy refill request
    for medications chosen by the user.

    The function calculates:
    - total quantity required for the chosen days
    - current supply available
    - quantity that actually needs to be refilled

    Returns:
        DataFrame:
        Pharmacy refill request list.
    """

    refill_columns = [
        "medication_name",
        "ingredients_substances",
        "medication_type",
        "dose_quantity",
        "dose_unit",
        "required_quantity",
        "current_supply",
        "refill_quantity",
        "refill_status"
    ]


    if medications_df.empty:

        return pd.DataFrame(
            columns=refill_columns
        )


    if not selected_medication_ids:

        return pd.DataFrame(
            columns=refill_columns
        )


    try:

        number_of_days = int(
            number_of_days
        )

    except (
        ValueError,
        TypeError
    ):

        return pd.DataFrame(
            columns=refill_columns
        )


    if number_of_days <= 0:

        return pd.DataFrame(
            columns=refill_columns
        )


    selected_ids = pd.to_numeric(
        pd.Series(
            selected_medication_ids
        ),
        errors="coerce"
    ).dropna()


    medication_ids = pd.to_numeric(
        medications_df[
            "medication_id"
        ],
        errors="coerce"
    )


    selected_df = medications_df[
        medication_ids.isin(
            selected_ids
        )
    ]


    refill_rows = []


    for _, medication in (
        selected_df.iterrows()
    ):

        required_quantity = (
            calculate_required_quantity(
                medication[
                    "dose_quantity"
                ],
                medication[
                    "dosage_frequency_value"
                ],
                medication[
                    "dosage_frequency_unit"
                ],
                number_of_days
            )
        )


        try:

            current_supply = float(
                medication[
                    "current_supply"
                ]
            )

            if current_supply < 0:
                current_supply = 0

        except (
            ValueError,
            TypeError
        ):

            current_supply = 0


        refill_quantity = max(
            required_quantity
            - current_supply,
            0
        )


        dose_unit = str(
            medication[
                "dose_unit"
            ]
        ).strip()


        # Pills/tablets/capsules are supplied as
        # whole physical units.
        if dose_unit.lower() in [
            "pill",
            "tablet",
            "capsule",
            "dose"
        ]:

            required_quantity = (
                math.ceil(
                    required_quantity
                )
            )

            refill_quantity = (
                math.ceil(
                    refill_quantity
                )
            )


        if refill_quantity > 0:

            refill_status = (
                "Refill Needed"
            )

        else:

            refill_status = (
                "Enough Supply"
            )


        refill_rows.append(
            {
                "medication_name":
                    medication[
                        "medication_name"
                    ],

                "ingredients_substances":
                    medication[
                        "ingredients_substances"
                    ],

                "medication_type":
                    medication[
                        "medication_type"
                    ],

                "dose_quantity":
                    medication[
                        "dose_quantity"
                    ],

                "dose_unit":
                    dose_unit,

                "required_quantity":
                    required_quantity,

                "current_supply":
                    current_supply,

                "refill_quantity":
                    refill_quantity,

                "refill_status":
                    refill_status
            }
        )


    return pd.DataFrame(
        refill_rows,
        columns=refill_columns
    )


# =========================================================
# SEARCH SAVED MEDICATIONS
# =========================================================

def search_saved_medications(
    medications_df,
    search_text
):
    """
    Search medications by:
    - medication name
    - active ingredient/substance
    - symptom tag
    """

    search_text = str(
        search_text
    ).strip().lower()


    if search_text == "":

        return pd.DataFrame(
            columns=medications_df.columns
        )


    name_match = (
        medications_df[
            "medication_name"
        ]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.contains(
            search_text,
            regex=False
        )
    )


    ingredient_match = (
        medications_df[
            "ingredients_substances"
        ]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.contains(
            search_text,
            regex=False
        )
    )


    symptom_match = (
        medications_df[
            "symptoms_tags"
        ]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.contains(
            search_text,
            regex=False
        )
    )


    matches = medications_df[
        name_match
        | ingredient_match
        | symptom_match
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
    Find saved medications containing
    the searched ingredient.

    Returns:
        list:
        Matching medication names.
    """

    search_text = str(
        search_text
    ).strip().lower()


    if search_text == "":
        return []


    ingredient_match = (
        medications_df[
            "ingredients_substances"
        ]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.contains(
            search_text,
            regex=False
        )
    )


    matching_medications = (
        medications_df.loc[
            ingredient_match,
            "medication_name"
        ]
        .tolist()
    )


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
    Calculate the next scheduled intake time.

    Returns:
        datetime or None.
    """

    if (
        pd.isna(
            start_time
        )
        or str(
            start_time
        ).strip() == ""
    ):

        return None


    try:

        start = datetime.strptime(
            str(
                start_time
            )[:5],
            "%H:%M"
        ).replace(
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day
        )


        frequency_value = float(
            frequency_value
        )


        if frequency_value <= 0:

            return None


        frequency_unit = str(
            frequency_unit
        ).strip().lower()


        if frequency_unit.startswith(
            "hour"
        ):

            interval = timedelta(
                hours=frequency_value
            )


        elif frequency_unit.startswith(
            "minute"
        ):

            interval = timedelta(
                minutes=frequency_value
            )


        else:

            return None


        next_time = start


        while (
            next_time
            <= datetime.now()
        ):

            next_time += interval


        return next_time


    except (
        ValueError,
        TypeError
    ):

        return None


# =========================================================
# DAILY 24-HOUR SCHEDULE
# =========================================================

def generate_daily_schedule(
    medications_df,
    schedule_date=None
):
    """
    Generate the chronological medication
    schedule for one calendar day.

    schedule_date is optional.
    If omitted, today's date is used.

    Returns:
        list:
        Scheduled medication doses.
    """

    schedule = []


    if schedule_date is None:

        target_date = (
            datetime.now().date()
        )

    else:

        try:

            target_date = (
                pd.to_datetime(
                    schedule_date
                ).date()
            )

        except (
            ValueError,
            TypeError
        ):

            return []


    for _, medication in (
        medications_df.iterrows()
    ):

        start_time = medication[
            "start_time"
        ]


        if (
            pd.isna(
                start_time
            )
            or str(
                start_time
            ).strip() == ""
        ):

            continue


        try:

            first_dose = datetime.strptime(
                str(
                    start_time
                )[:5],
                "%H:%M"
            )


            frequency_value = float(
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
            ).strip().lower()


            if frequency_unit.startswith(
                "hour"
            ):

                interval = timedelta(
                    hours=frequency_value
                )


            elif frequency_unit.startswith(
                "minute"
            ):

                interval = timedelta(
                    minutes=frequency_value
                )


            else:

                continue


            current_dose = (
                datetime.combine(
                    target_date,
                    first_dose.time()
                )
            )


            end_of_day = (
                datetime.combine(
                    target_date
                    + timedelta(
                        days=1
                    ),
                    datetime.min.time()
                )
            )


            while (
                current_dose
                < end_of_day
            ):

                schedule.append(
                    {
                        "medication_id":
                            medication[
                                "medication_id"
                            ],

                        "medication_name":
                            medication[
                                "medication_name"
                            ],

                        "time":
                            current_dose,

                        "dose_quantity":
                            medication[
                                "dose_quantity"
                            ],

                        "dose_unit":
                            medication[
                                "dose_unit"
                            ]
                    }
                )


                current_dose += (
                    interval
                )


        except (
            ValueError,
            TypeError
        ):

            continue


    schedule.sort(
        key=lambda item:
            item["time"]
    )


    return schedule


# =========================================================
# LOG MEDICATION INTAKE
# =========================================================

def log_medication_intake(
    history_df,
    medication_id,
    medication_name,
    scheduled_time,
    status="Taken",
    recorded_time=None
):
    """
    Record an actual medication intake event.

    A scheduled dose can be recorded as:
        Taken
        Missed

    If the same scheduled dose already exists,
    its record is updated instead of duplicated.

    Returns:
        DataFrame:
        Updated intake history.
    """

    status = str(
        status
    ).strip().title()


    if status not in [
        "Taken",
        "Missed"
    ]:

        return history_df


    scheduled_datetime = (
        pd.to_datetime(
            scheduled_time,
            errors="coerce"
        )
    )


    if pd.isna(
        scheduled_datetime
    ):

        return history_df


    if recorded_time is None:

        recorded_datetime = (
            datetime.now()
        )

    else:

        recorded_datetime = (
            pd.to_datetime(
                recorded_time,
                errors="coerce"
            )
        )

        if pd.isna(
            recorded_datetime
        ):

            recorded_datetime = (
                datetime.now()
            )


    scheduled_text = (
        scheduled_datetime.strftime(
            "%Y-%m-%d %H:%M"
        )
    )

    recorded_text = (
        recorded_datetime.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )


    if history_df is None:

        history_df = (
            load_intake_history()
        )


    history_df = (
        history_df.copy()
    )


    # Ensure expected columns exist.
    for column in intake_history_columns:

        if column not in history_df.columns:

            history_df[
                column
            ] = ""


    if not history_df.empty:

        existing_schedule = (
            pd.to_datetime(
                history_df[
                    "scheduled_time"
                ],
                errors="coerce"
            )
            .dt.strftime(
                "%Y-%m-%d %H:%M"
            )
        )


        existing_ids = (
            pd.to_numeric(
                history_df[
                    "medication_id"
                ],
                errors="coerce"
            )
        )


        try:

            medication_id_number = float(
                medication_id
            )

        except (
            ValueError,
            TypeError
        ):

            medication_id_number = None


        if medication_id_number is not None:

            existing_mask = (
                existing_ids.eq(
                    medication_id_number
                )
                & existing_schedule.eq(
                    scheduled_text
                )
            )


            if existing_mask.any():

                existing_index = (
                    history_df.index[
                        existing_mask
                    ][0]
                )


                history_df.at[
                    existing_index,
                    "status"
                ] = status


                history_df.at[
                    existing_index,
                    "recorded_time"
                ] = recorded_text


                save_intake_history(
                    history_df
                )


                return history_df


    # Create next intake ID.
    if history_df.empty:

        intake_id = 1

    else:

        existing_intake_ids = (
            pd.to_numeric(
                history_df[
                    "intake_id"
                ],
                errors="coerce"
            )
        )


        max_intake_id = (
            existing_intake_ids.max()
        )


        if pd.isna(
            max_intake_id
        ):

            intake_id = 1

        else:

            intake_id = (
                int(
                    max_intake_id
                )
                + 1
            )


    new_history_record = {

        "intake_id":
            intake_id,

        "medication_id":
            medication_id,

        "medication_name":
            medication_name,

        "scheduled_time":
            scheduled_text,

        "status":
            status,

        "recorded_time":
            recorded_text
    }


    history_df.loc[
        len(
            history_df
        )
    ] = new_history_record


    save_intake_history(
        history_df
    )


    return history_df


# =========================================================
# DAILY INTAKE STATUS
# =========================================================

def get_daily_intake_status(
    medications_df,
    history_df=None,
    reference_time=None,
    grace_minutes=60
):
    """
    Compare today's schedule against intake history.

    Status values:
        Taken
        Missed
        Upcoming
        Due
        Overdue

    A dose is considered Overdue only after
    grace_minutes have passed.

    Returns:
        DataFrame:
        Today's scheduled doses and statuses.
    """

    status_columns = [
        "medication_id",
        "medication_name",
        "scheduled_time",
        "dose_quantity",
        "dose_unit",
        "status",
        "recorded_time"
    ]


    if reference_time is None:

        reference_datetime = (
            datetime.now()
        )

    else:

        reference_datetime = (
            pd.to_datetime(
                reference_time,
                errors="coerce"
            )
        )


        if pd.isna(
            reference_datetime
        ):

            reference_datetime = (
                datetime.now()
            )


    try:

        grace_minutes = int(
            grace_minutes
        )

    except (
        ValueError,
        TypeError
    ):

        grace_minutes = 60


    if grace_minutes < 0:

        grace_minutes = 0


    if history_df is None:

        history_df = (
            load_intake_history()
        )


    schedule = (
        generate_daily_schedule(
            medications_df,
            reference_datetime.date()
        )
    )


    if not schedule:

        return pd.DataFrame(
            columns=status_columns
        )


    status_rows = []


    for dose in schedule:

        scheduled_datetime = dose[
            "time"
        ]


        scheduled_text = (
            scheduled_datetime.strftime(
                "%Y-%m-%d %H:%M"
            )
        )


        matched_history = (
            pd.DataFrame()
        )


        if not history_df.empty:

            history_ids = (
                pd.to_numeric(
                    history_df[
                        "medication_id"
                    ],
                    errors="coerce"
                )
            )


            history_schedule = (
                pd.to_datetime(
                    history_df[
                        "scheduled_time"
                    ],
                    errors="coerce"
                )
                .dt.strftime(
                    "%Y-%m-%d %H:%M"
                )
            )


            try:

                medication_id_number = float(
                    dose[
                        "medication_id"
                    ]
                )

            except (
                ValueError,
                TypeError
            ):

                medication_id_number = None


            if medication_id_number is not None:

                history_mask = (
                    history_ids.eq(
                        medication_id_number
                    )
                    & history_schedule.eq(
                        scheduled_text
                    )
                )


                matched_history = (
                    history_df[
                        history_mask
                    ]
                )


        if not matched_history.empty:

            latest_record = (
                matched_history.iloc[
                    -1
                ]
            )


            dose_status = str(
                latest_record[
                    "status"
                ]
            )


            recorded_time = (
                latest_record[
                    "recorded_time"
                ]
            )


        else:

            recorded_time = ""


            if (
                reference_datetime
                < scheduled_datetime
            ):

                dose_status = (
                    "Upcoming"
                )


            elif (
                reference_datetime
                <= scheduled_datetime
                + timedelta(
                    minutes=
                        grace_minutes
                )
            ):

                dose_status = (
                    "Due"
                )


            else:

                dose_status = (
                    "Overdue"
                )


        status_rows.append(
            {
                "medication_id":
                    dose[
                        "medication_id"
                    ],

                "medication_name":
                    dose[
                        "medication_name"
                    ],

                "scheduled_time":
                    scheduled_datetime,

                "dose_quantity":
                    dose[
                        "dose_quantity"
                    ],

                "dose_unit":
                    dose[
                        "dose_unit"
                    ],

                "status":
                    dose_status,

                "recorded_time":
                    recorded_time
            }
        )


    return pd.DataFrame(
        status_rows,
        columns=status_columns
    )


# =========================================================
# UNRECORDED / OVERDUE DOSE ALERTS
# =========================================================

def get_unrecorded_dose_alerts(
    medications_df,
    history_df=None,
    reference_time=None,
    grace_minutes=60
):
    """
    Return alert messages for scheduled doses
    that are overdue and have not been recorded.

    Returns:
        list:
        Human-readable alert messages.
    """

    daily_status = (
        get_daily_intake_status(
            medications_df,
            history_df,
            reference_time,
            grace_minutes
        )
    )


    if daily_status.empty:
        return []


    overdue_doses = (
        daily_status[
            daily_status[
                "status"
            ] == "Overdue"
        ]
    )


    alerts = []


    for _, dose in (
        overdue_doses.iterrows()
    ):

        scheduled_time = (
            pd.to_datetime(
                dose[
                    "scheduled_time"
                ]
            )
        )


        alerts.append(
            f"{dose['medication_name']} was scheduled "
            f"for {scheduled_time.strftime('%I:%M %p')} "
            "and has not been recorded as taken."
        )


    return alerts


# =========================================================
# EXPIRATION CHECK
# =========================================================

def check_expiration_status(
    expiration_date,
    warning_days=7
):
    """
    Check whether medication is:
        Expired
        Expiring Soon
        OK
        Unknown
    """

    if (
        pd.isna(
            expiration_date
        )
        or str(
            expiration_date
        ).strip() == ""
    ):

        return "Unknown"


    try:

        expiration = (
            pd.to_datetime(
                expiration_date
            ).date()
        )


        today = (
            datetime.now().date()
        )


        days_remaining = (
            expiration
            - today
        ).days


        if days_remaining < 0:

            return "Expired"


        elif (
            days_remaining
            <= warning_days
        ):

            return "Expiring Soon"


        else:

            return "OK"


    except (
        ValueError,
        TypeError
    ):

        return "Unknown"


# =========================================================
# LOW SUPPLY CHECK
# =========================================================

def check_low_supply(
    current_supply,
    refill_threshold
):
    """
    Check whether medication supply
    has reached the refill threshold.

    Returns:
        bool
    """

    try:

        current_supply = float(
            current_supply
        )

        refill_threshold = float(
            refill_threshold
        )


        if (
            current_supply < 0
            or refill_threshold < 0
        ):

            return False


        return (
            current_supply
            <= refill_threshold
        )


    except (
        ValueError,
        TypeError
    ):

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
    Delete one, multiple,
    or all medications.

    Returns:
        DataFrame:
        Updated medication records.
    """

    if delete_all:

        return (
            medications_df
            .iloc[
                0:0
            ]
            .copy()
        )


    if medication_ids:

        numeric_ids = (
            pd.to_numeric(
                medications_df[
                    "medication_id"
                ],
                errors="coerce"
            )
        )


        selected_ids = (
            pd.to_numeric(
                pd.Series(
                    medication_ids
                ),
                errors="coerce"
            )
            .dropna()
        )


        updated_df = (
            medications_df[
                ~numeric_ids.isin(
                    selected_ids
                )
            ]
            .copy()
        )


        return updated_df


    return medications_df.copy()