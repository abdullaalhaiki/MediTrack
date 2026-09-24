import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

import myutils


# -----------------------------------------
# PAGE SETTINGS
# -----------------------------------------

st.set_page_config(
    page_title="MediTrack",
    page_icon="💊",
    layout="wide"
)


# -----------------------------------------
# LOAD SAVED MEDICATIONS
# -----------------------------------------

medications_df = myutils.load_medications()


# -----------------------------------------
# HEADER
# -----------------------------------------

st.title("💊 MediTrack")
st.caption("Digital Medication Tracker & Personal Health Record")


# -----------------------------------------
# SIDEBAR MENU
# -----------------------------------------

menu = st.sidebar.radio(
    "Menu",
    [
        "Add Medication",
        "Search Medications",
        "My Medications",
        "Wellness Spotlight"
    ]
)


# =========================================
# 1. ADD MEDICATION
# =========================================

if menu == "Add Medication":

    st.header("Add a New Medication")

    with st.form("add_medication_form"):

        medication_name = st.text_input(
            "Medication Name",
            placeholder="Example: Ibuprofen"
        )

        ingredients_substances = st.text_input(
            "Active Ingredients / Interacting Substances",
            placeholder="Example: Ibuprofen, Caffeine"
        )

        symptoms_tags = st.text_input(
            "Symptoms / Tags",
            placeholder="Example: headache, fever, pain"
        )

        col1, col2 = st.columns(2)

        with col1:
            dosage_frequency_value = st.number_input(
                "Dosage Frequency",
                min_value=1,
                value=8,
                step=1
            )

        with col2:
            dosage_frequency_unit = st.selectbox(
                "Frequency Unit",
                ["Hours", "Minutes"]
            )

        usage_safety_instructions = st.text_area(
            "Usage & Safety Instructions",
            placeholder="Example: Take with food"
        )

        urgency_level = st.selectbox(
            "Urgency / Critical Level",
            ["Low", "Medium", "High"]
        )

        start_time = st.time_input(
            "First Dose / Start Time"
        )

        col3, col4 = st.columns(2)

        with col3:
            current_supply = st.number_input(
                "Current Supply",
                min_value=0,
                value=0,
                step=1
            )

        with col4:
            refill_threshold = st.number_input(
                "Refill Threshold",
                min_value=0,
                value=5,
                step=1
            )

        expiration_date = st.date_input(
            "Expiration Date",
            value=(
                datetime.now()
                + timedelta(days=365)
            ).date()
        )

        submitted = st.form_submit_button(
            "Add Medication"
        )

    if submitted:

        if medication_name.strip() == "":
            st.error("Please enter a medication name.")

        elif ingredients_substances.strip() == "":
            st.error(
                "Please enter at least one active ingredient."
            )

        elif myutils.is_duplicate_medication(
            medications_df,
            medication_name
        ):
            st.warning(
                f"{medication_name} is already saved."
            )

        else:

            medications_df = myutils.add_medication(
                medications_df,
                medication_name,
                ingredients_substances,
                dosage_frequency_value,
                dosage_frequency_unit,
                usage_safety_instructions,
                urgency_level,
                symptoms_tags,
                start_time.strftime("%H:%M"),
                current_supply,
                refill_threshold,
                expiration_date.isoformat()
            )

            st.success(
                f"{medication_name} added successfully."
            )
            # =========================================
# 2. SEARCH MEDICATIONS
# =========================================

elif menu == "Search Medications":

    st.header("Search Medications")

    search_text = st.text_input(
        "Search by medication name, active ingredient, or symptom",
        placeholder="Example: paracetamol, headache, Panadol"
    )

    if st.button("Search"):

        if search_text.strip() == "":
            st.warning("Please enter a search term.")

        else:
            results = myutils.search_saved_medications(
                medications_df,
                search_text
            )

            if results.empty:
                st.info("No matching saved medications found.")

            else:
                st.success(
                    f"{len(results)} matching medication(s) found."
                )

                st.dataframe(
                    results[
                        [
                            "medication_name",
                            "ingredients_substances",
                            "symptoms_tags",
                            "dosage_frequency_value",
                            "dosage_frequency_unit",
                            "urgency_level"
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True
                )

                risk_medications = (
                    myutils.check_shared_ingredient_risk(
                        medications_df,
                        search_text
                    )
                )

                if len(risk_medications) > 1:
                    st.warning(
                        "Potential overlapping ingredient risk: "
                        + ", ".join(risk_medications)
                        + " contain the searched ingredient."
                    )
    st.divider()

    st.subheader("Search External Medication Database")

    api_search_text = st.text_input(
        "Enter a medication name to search the drug database",
        placeholder="Example: Aspirin, Ibuprofen",
        key="api_search"
    )

    if st.button(
        "Search Drug Database",
        key="api_search_button"
    ):

        if api_search_text.strip() == "":
            st.warning(
                "Please enter a medication name."
            )

        else:

            with st.spinner(
                "Searching external medication database..."
            ):

                raw_results = (
                    myutils.search_medication_api(
                        api_search_text
                    )
                )

                api_results = (
                    myutils.process_api_results(
                        raw_results
                    )
                )

            if not api_results:

                st.info(
                    "No medication information found."
                )

            else:

                st.success(
                    f"{len(api_results)} result(s) found."
                )

                for index, medication in enumerate(
                    api_results[:5],
                    start=1
                ):

                    title = (
                        medication["brand_name"]
                        or medication["generic_name"]
                    )

                    with st.expander(
                        f"{index}. {title}"
                    ):

                        st.write(
                            "**Generic Name:**",
                            medication["generic_name"]
                        )

                        st.write(
                            "**Active Substance:**",
                            medication["substances"]
                        )

                        route = medication["route"]

                        if isinstance(route, list):
                            route = ", ".join(route)

                        st.write(
                            "**Route:**",
                            route
                        )

                        st.write(
                            "**Dosage Form:**",
                            medication["dosage_form"]
                        )

                        st.write(
                            "**Purpose:**",
                            medication["purpose"]
                        )

                        st.write(
                            "**Indications / Usage:**",
                            medication[
                                "indications_and_usage"
                            ]
                        )
# =========================================
# 3. MY MEDICATIONS
# =========================================

elif menu == "My Medications":

    st.header("My Medications")

    if medications_df.empty:

        st.info("No medications have been added yet.")

    else:

        medication_view = medications_df.copy()

        next_intakes = []
        expiration_statuses = []
        supply_statuses = []


        # ---------------------------------
        # CALCULATE STATUS FOR EACH MEDICINE
        # ---------------------------------

        for _, medication in medication_view.iterrows():

            # Next intake
            next_intake = myutils.calculate_next_intake(
                medication["start_time"],
                medication["dosage_frequency_value"],
                medication["dosage_frequency_unit"]
            )

            if next_intake is not None:

                next_intakes.append(
                    next_intake.strftime("%I:%M %p")
                )

            else:
                next_intakes.append("Not set")


            # Expiration status
            expiration_status = (
                myutils.check_expiration_status(
                    medication["expiration_date"]
                )
            )

            expiration_statuses.append(
                expiration_status
            )


            # Supply status
            current_supply = medication[
                "current_supply"
            ]

            refill_threshold = medication[
                "refill_threshold"
            ]

            if (
                pd.isna(current_supply)
                or pd.isna(refill_threshold)
            ):

                supply_statuses.append(
                    "Not set"
                )

            elif myutils.check_low_supply(
                current_supply,
                refill_threshold
            ):

                supply_statuses.append(
                    "Low"
                )

            else:
                supply_statuses.append(
                    "OK"
                )


        # Add calculated columns
        medication_view["next_intake"] = (
            next_intakes
        )

        medication_view["expiration_status"] = (
            expiration_statuses
        )

        medication_view["supply_status"] = (
            supply_statuses
        )


        # ---------------------------------
        # DISPLAY MEDICATION TABLE
        # ---------------------------------

        st.subheader("Medication List")

        st.dataframe(
            medication_view[
                [
                    "medication_name",
                    "ingredients_substances",
                    "dosage_frequency_value",
                    "dosage_frequency_unit",
                    "next_intake",
                    "urgency_level",
                    "expiration_status",
                    "supply_status"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )


        # =================================
        # MEDICATION ALERTS
        # =================================

        st.subheader("Medication Alerts")

        alerts_found = False

        for _, medication in medication_view.iterrows():

            name = medication[
                "medication_name"
            ]

            expiry = medication[
                "expiration_status"
            ]

            supply = medication[
                "supply_status"
            ]

            if expiry == "Expired":

                st.error(
                    f"{name}: This medication has expired."
                )

                alerts_found = True

            elif expiry == "Expiring Soon":

                st.warning(
                    f"{name}: This medication expires "
                    "within 7 days."
                )

                alerts_found = True

            if supply == "Low":

                st.warning(
                    f"{name}: Supply has reached "
                    "the refill threshold."
                )

                alerts_found = True


        if not alerts_found:

            st.success(
                "No medication alerts at this time."
            )


        # =================================
        # 24-HOUR DAILY SCHEDULE
        # =================================

        st.subheader("24-Hour Daily Schedule")

        daily_schedule = (
            myutils.generate_daily_schedule(
                medications_df
            )
        )

        if not daily_schedule:

            st.info(
                "No medication schedule is available."
            )

        else:

            schedule_data = []

            for dose in daily_schedule:

                schedule_data.append(
                    {
                        "Time":
                            dose["time"].strftime(
                                "%I:%M %p"
                            ),
                        "Medication":
                            dose["medication_name"]
                    }
                )

            schedule_df = pd.DataFrame(
                schedule_data
            )

            st.dataframe(
                schedule_df,
                use_container_width=True,
                hide_index=True
            )


        # =================================
        # DELETE MEDICATIONS
        # =================================

        st.subheader("Manage Medications")

        medication_options = {}

        for _, medication in medications_df.iterrows():

            label = (
                f"{int(medication['medication_id'])}"
                f" - {medication['medication_name']}"
            )

            medication_options[label] = (
                medication["medication_id"]
            )


        selected_medications = st.multiselect(
            "Select medication(s) to delete",
            list(medication_options.keys())
        )


        if st.button(
            "Delete Selected Medication(s)"
        ):

            if not selected_medications:

                st.warning(
                    "Please select at least one medication."
                )

            else:

                selected_ids = [
                    medication_options[item]
                    for item in selected_medications
                ]

                updated_df = (
                    myutils.delete_medications(
                        medications_df,
                        selected_ids
                    )
                )

                myutils.save_medications(
                    updated_df
                )

                st.success(
                    "Selected medication(s) deleted."
                )

                st.rerun()


        # ---------------------------------
        # DELETE ALL
        # ---------------------------------

        confirm_delete_all = st.checkbox(
            "I confirm that I want to delete all medications."
        )

        if st.button(
            "Delete All Medications"
        ):

            if not confirm_delete_all:

                st.warning(
                    "Please confirm before deleting all medications."
                )

            else:

                updated_df = (
                    myutils.delete_medications(
                        medications_df,
                        delete_all=True
                    )
                )

                myutils.save_medications(
                    updated_df
                )

                st.success(
                    "All medications deleted."
                )

                st.rerun()
# =========================================
# 4. WELLNESS SPOTLIGHT
# =========================================

elif menu == "Wellness Spotlight":

    st.header("Wellness & Medication Spotlight")

    st.write(
        "Get a random wellness tip or medication spotlight "
        "generated by MediTrack."
    )

    # Generate one spotlight when the page is opened
    if "wellness_spotlight" not in st.session_state:

        with st.spinner("Generating your spotlight..."):

            st.session_state["wellness_spotlight"] = (
                myutils.get_random_wellness_spotlight()
            )


    spotlight = st.session_state[
        "wellness_spotlight"
    ]


    # Display the type
    st.subheader(
        spotlight["type"]
    )

    # Display the generated content
    st.info(
        spotlight["content"]
    )


    # Generate a new random spotlight
    if st.button("Generate New Spotlight"):

        with st.spinner(
            "Generating a new spotlight..."
        ):

            st.session_state[
                "wellness_spotlight"
            ] = (
                myutils.get_random_wellness_spotlight()
            )

        st.rerun()


    st.caption(
        "This information is for general educational purposes only "
        "and is not a substitute for professional medical advice."
    )