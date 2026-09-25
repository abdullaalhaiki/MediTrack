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
# LOAD SAVED DATA
# -----------------------------------------

medications_df = myutils.load_medications()
intake_history_df = myutils.load_intake_history()


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

        medication_type = st.selectbox(
            "Medication Type",
            [
                "Prescription",
                "Over-the-Counter (OTC)",
                "Supplement",
                "First Aid"
            ]
        )

        dose_col1, dose_col2 = st.columns(2)

        with dose_col1:
            dose_quantity = st.number_input(
                "Dose Quantity",
                min_value=0.5,
                value=1.0,
                step=0.5
            )

        with dose_col2:
            dose_unit = st.selectbox(
                "Dose Unit",
                [
                    "Pill",
                    "Tablet",
                    "Capsule",
                    "mL",
                    "mg",
                    "Dose"
                ]
            )

        frequency_col1, frequency_col2 = st.columns(2)

        with frequency_col1:
            dosage_frequency_value = st.number_input(
                "Dosage Frequency",
                min_value=1,
                value=8,
                step=1
            )

        with frequency_col2:
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

        compliance_rating = st.select_slider(
            "Self-Reported Compliance Rating",
            options=[1, 2, 3, 4, 5],
            value=3,
            format_func=lambda rating: f"{rating} ⭐"
        )

        start_time = st.time_input(
            "First Dose / Start Time"
        )

        supply_col1, supply_col2 = st.columns(2)

        with supply_col1:
            current_supply = st.number_input(
                "Current Supply",
                min_value=0.0,
                value=0.0,
                step=0.5
            )

        with supply_col2:
            refill_threshold = st.number_input(
                "Refill Threshold",
                min_value=0.0,
                value=5.0,
                step=0.5
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
            st.error(
                "Please enter a medication name."
            )

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
                medication_type,
                dose_quantity,
                dose_unit,
                start_time.strftime("%H:%M"),
                current_supply,
                refill_threshold,
                expiration_date.isoformat(),
                compliance_rating
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
            st.warning(
                "Please enter a search term."
            )

        else:
            results = myutils.search_saved_medications(
                medications_df,
                search_text
            )

            if results.empty:
                st.info(
                    "No matching saved medications found."
                )

            else:
                st.success(
                    f"{len(results)} matching medication(s) found."
                )

                st.dataframe(
                    results[
                        [
                            "medication_name",
                            "medication_type",
                            "ingredients_substances",
                            "symptoms_tags",
                            "dose_quantity",
                            "dose_unit",
                            "dosage_frequency_value",
                            "dosage_frequency_unit",
                            "urgency_level",
                            "compliance_rating"
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

                        st.write(
                            "**Warnings:**",
                            medication["warnings"]
                        )


# =========================================
# 3. MY MEDICATIONS
# =========================================

elif menu == "My Medications":

    st.header("My Medications")

    if medications_df.empty:
        st.info(
            "No medications have been added yet."
        )

    else:
        medication_view = medications_df.copy()

        next_intakes = []
        expiration_statuses = []
        supply_statuses = []

        # ---------------------------------
        # CALCULATE STATUS FOR EACH MEDICINE
        # ---------------------------------

        for _, medication in medication_view.iterrows():

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

            expiration_status = (
                myutils.check_expiration_status(
                    medication["expiration_date"]
                )
            )

            expiration_statuses.append(
                expiration_status
            )

            current_supply_value = medication[
                "current_supply"
            ]

            refill_threshold_value = medication[
                "refill_threshold"
            ]

            if (
                pd.isna(current_supply_value)
                or pd.isna(refill_threshold_value)
                or str(current_supply_value).strip() == ""
                or str(refill_threshold_value).strip() == ""
            ):
                supply_statuses.append(
                    "Not set"
                )

            elif myutils.check_low_supply(
                current_supply_value,
                refill_threshold_value
            ):
                supply_statuses.append(
                    "Low"
                )

            else:
                supply_statuses.append(
                    "OK"
                )

        medication_view["next_intake"] = (
            next_intakes
        )

        medication_view["expiration_status"] = (
            expiration_statuses
        )

        medication_view["supply_status"] = (
            supply_statuses
        )


        # =================================
        # MEDICATION LIST + COMPLIANCE SORT
        # =================================

        st.subheader("Medication List")

        sort_option = st.selectbox(
            "Sort Medication List",
            [
                "Default Order",
                "Highest Compliance Rating First"
            ],
            key="medication_sort"
        )

        if (
            sort_option
            == "Highest Compliance Rating First"
        ):
            medication_view = (
                myutils.sort_medications_by_compliance(
                    medication_view
                )
            )

        st.dataframe(
            medication_view[
                [
                    "medication_name",
                    "medication_type",
                    "ingredients_substances",
                    "dose_quantity",
                    "dose_unit",
                    "dosage_frequency_value",
                    "dosage_frequency_unit",
                    "next_intake",
                    "urgency_level",
                    "compliance_rating",
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

                dose_quantity_value = dose[
                    "dose_quantity"
                ]

                dose_unit_value = dose[
                    "dose_unit"
                ]

                if (
                    pd.isna(dose_quantity_value)
                    or str(dose_quantity_value).strip() == ""
                    or pd.isna(dose_unit_value)
                    or str(dose_unit_value).strip() == ""
                ):
                    dose_text = "Not set"

                else:
                    dose_text = (
                        f"{dose_quantity_value} "
                        f"{dose_unit_value}"
                    )

                schedule_data.append(
                    {
                        "Time":
                            dose["time"].strftime(
                                "%I:%M %p"
                            ),
                        "Medication":
                            dose["medication_name"],
                        "Dose":
                            dose_text
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


        # =========================================
        # MEDICATION QUANTITY CALCULATOR
        # =========================================

        st.subheader(
            "Medication Quantity Calculator"
        )

        quantity_medication = st.selectbox(
            "Select a medication",
            medications_df[
                "medication_name"
            ].tolist(),
            key="quantity_medication"
        )

        number_of_days = st.number_input(
            "Number of days",
            min_value=1,
            value=30,
            step=1,
            key="quantity_days"
        )

        if st.button(
            "Calculate Required Quantity",
            key="calculate_quantity_button"
        ):
            selected_medication = medications_df[
                medications_df[
                    "medication_name"
                ] == quantity_medication
            ].iloc[0]

            dose_quantity_value = selected_medication[
                "dose_quantity"
            ]

            dose_unit_value = selected_medication[
                "dose_unit"
            ]

            if (
                pd.isna(dose_quantity_value)
                or str(dose_quantity_value).strip() == ""
                or pd.isna(dose_unit_value)
                or str(dose_unit_value).strip() == ""
            ):
                st.warning(
                    "Dose quantity or dose unit is not set "
                    "for this medication."
                )

            else:
                required_quantity = (
                    myutils.calculate_required_quantity(
                        dose_quantity_value,
                        selected_medication[
                            "dosage_frequency_value"
                        ],
                        selected_medication[
                            "dosage_frequency_unit"
                        ],
                        number_of_days
                    )
                )

                if required_quantity <= 0:
                    st.warning(
                        "The required quantity could not be calculated. "
                        "Check the medication dose and frequency."
                    )

                else:
                    st.success(
                        f"You need {required_quantity:g} "
                        f"{dose_unit_value}(s) "
                        f"for {number_of_days} days."
                    )


        # =========================================
        # PHARMACY REFILL REQUEST LIST
        # =========================================

        st.subheader(
            "Pharmacy Refill Request List"
        )

        refill_options = {}

        for _, medication in medications_df.iterrows():
            label = (
                f"{medication['medication_name']} "
                f"({medication['ingredients_substances']})"
            )

            refill_options[label] = (
                medication["medication_id"]
            )

        selected_refill_labels = st.multiselect(
            "Select medication(s) for the refill request",
            list(refill_options.keys()),
            key="refill_multiselect"
        )

        refill_days = st.number_input(
            "Refill supply for how many days?",
            min_value=1,
            value=30,
            step=1,
            key="refill_days"
        )

        if st.button(
            "Generate Refill Request",
            key="generate_refill_request"
        ):

            if not selected_refill_labels:
                st.warning(
                    "Please select at least one medication."
                )

            else:
                selected_refill_ids = [
                    refill_options[label]
                    for label in selected_refill_labels
                ]

                selected_refill_df = medications_df[
                    pd.to_numeric(
                        medications_df[
                            "medication_id"
                        ],
                        errors="coerce"
                    ).isin(
                        pd.to_numeric(
                            pd.Series(
                                selected_refill_ids
                            ),
                            errors="coerce"
                        ).dropna()
                    )
                ]

                missing_refill_info = (
                    selected_refill_df[
                        "dose_quantity"
                    ].isna()
                    | selected_refill_df[
                        "dose_unit"
                    ].isna()
                    | selected_refill_df[
                        "dosage_frequency_value"
                    ].isna()
                    | selected_refill_df[
                        "dosage_frequency_unit"
                    ].isna()
                    | selected_refill_df[
                        "current_supply"
                    ].isna()
                    | selected_refill_df[
                        "dose_quantity"
                    ].astype(str).str.strip().eq("")
                    | selected_refill_df[
                        "dose_unit"
                    ].astype(str).str.strip().eq("")
                    | selected_refill_df[
                        "dosage_frequency_value"
                    ].astype(str).str.strip().eq("")
                    | selected_refill_df[
                        "dosage_frequency_unit"
                    ].astype(str).str.strip().eq("")
                    | selected_refill_df[
                        "current_supply"
                    ].astype(str).str.strip().eq("")
                )

                if missing_refill_info.any():
                    missing_names = (
                        selected_refill_df.loc[
                            missing_refill_info,
                            "medication_name"
                        ]
                        .astype(str)
                        .tolist()
                    )

                    st.warning(
                        "Dose, frequency, or current-supply information "
                        "is missing for: "
                        + ", ".join(missing_names)
                        + ". Complete these medication details before "
                        "calculating an accurate refill request."
                    )

                else:
                    refill_df = (
                        myutils.generate_pharmacy_refill_list(
                            medications_df,
                            selected_refill_ids,
                            refill_days
                        )
                    )

                    if refill_df.empty:
                        st.info(
                            "No refill request could be generated."
                        )

                    else:
                        st.dataframe(
                            refill_df[
                                [
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
                            ],
                            use_container_width=True,
                            hide_index=True
                        )


        # =========================================
        # TODAY'S DOSE TRACKER
        # =========================================

        st.subheader("Today's Dose Tracker")

        st.caption(
            "A dose becomes Overdue only after the default "
            "60-minute grace period if it has not been recorded."
        )

        daily_status_df = (
            myutils.get_daily_intake_status(
                medications_df,
                intake_history_df
            )
        )

        overdue_alerts = (
            myutils.get_unrecorded_dose_alerts(
                medications_df,
                intake_history_df
            )
        )

        if overdue_alerts:
            for alert in overdue_alerts:
                st.warning(alert)

        if daily_status_df.empty:
            st.info(
                "No scheduled doses are available for today."
            )

        else:
            for _, dose in daily_status_df.iterrows():

                scheduled_time = pd.to_datetime(
                    dose["scheduled_time"]
                )

                dose_status = str(
                    dose["status"]
                )

                dose_quantity_display = (
                    dose["dose_quantity"]
                )

                dose_unit_display = (
                    dose["dose_unit"]
                )

                if (
                    pd.isna(dose_quantity_display)
                    or str(dose_quantity_display).strip() == ""
                    or pd.isna(dose_unit_display)
                    or str(dose_unit_display).strip() == ""
                ):
                    dose_display_text = "Dose not set"

                else:
                    dose_display_text = (
                        f"{dose_quantity_display} "
                        f"{dose_unit_display}"
                    )

                row_col1, row_col2, row_col3, row_col4, row_col5 = (
                    st.columns(
                        [1.4, 2.2, 1.5, 1.1, 1.1]
                    )
                )

                with row_col1:
                    st.write(
                        scheduled_time.strftime(
                            "%I:%M %p"
                        )
                    )

                with row_col2:
                    st.write(
                        dose["medication_name"]
                    )

                with row_col3:
                    st.write(
                        f"{dose_display_text} — "
                        f"{dose_status}"
                    )

                medication_id = dose[
                    "medication_id"
                ]

                button_suffix = (
                    f"{medication_id}_"
                    f"{scheduled_time.strftime('%Y%m%d%H%M')}"
                )

                can_record = (
                    dose_status
                    not in [
                        "Taken",
                        "Missed",
                        "Upcoming"
                    ]
                )

                with row_col4:
                    if can_record:
                        if st.button(
                            "Taken",
                            key=f"taken_{button_suffix}"
                        ):
                            myutils.log_medication_intake(
                                intake_history_df,
                                medication_id,
                                dose[
                                    "medication_name"
                                ],
                                scheduled_time,
                                status="Taken"
                            )

                            st.rerun()
                    else:
                        st.caption("—")

                with row_col5:
                    if can_record:
                        if st.button(
                            "Missed",
                            key=f"missed_{button_suffix}"
                        ):
                            myutils.log_medication_intake(
                                intake_history_df,
                                medication_id,
                                dose[
                                    "medication_name"
                                ],
                                scheduled_time,
                                status="Missed"
                            )

                            st.rerun()
                    else:
                        st.caption("—")

                st.divider()


        # =========================================
        # INTAKE HISTORY
        # =========================================

        st.subheader("Intake History")

        intake_history_df = (
            myutils.load_intake_history()
        )

        if intake_history_df.empty:
            st.info(
                "No medication intake has been recorded yet."
            )

        else:
            history_display = (
                intake_history_df.copy()
            )

            history_display[
                "_recorded_datetime"
            ] = pd.to_datetime(
                history_display[
                    "recorded_time"
                ],
                errors="coerce"
            )

            history_display = (
                history_display.sort_values(
                    by="_recorded_datetime",
                    ascending=False,
                    na_position="last"
                )
            )

            scheduled_display = pd.to_datetime(
                history_display[
                    "scheduled_time"
                ],
                errors="coerce"
            )

            recorded_display = pd.to_datetime(
                history_display[
                    "recorded_time"
                ],
                errors="coerce"
            )

            history_display[
                "scheduled_time"
            ] = scheduled_display.dt.strftime(
                "%Y-%m-%d %I:%M %p"
            )

            history_display[
                "recorded_time"
            ] = recorded_display.dt.strftime(
                "%Y-%m-%d %I:%M:%S %p"
            )

            st.dataframe(
                history_display[
                    [
                        "medication_name",
                        "scheduled_time",
                        "status",
                        "recorded_time"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )


        # =========================================
        # MANAGE MEDICATIONS
        # =========================================

        st.subheader("Manage Medications")

        medication_options = {}

        for _, medication in medications_df.iterrows():
            label = (
                f"{int(float(medication['medication_id']))}"
                f" - {medication['medication_name']}"
            )

            medication_options[label] = (
                medication["medication_id"]
            )

        selected_medications = st.multiselect(
            "Select medication(s) to delete",
            list(medication_options.keys()),
            key="delete_multiselect"
        )

        if st.button(
            "Delete Selected Medication(s)",
            key="delete_selected_button"
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

        confirm_delete_all = st.checkbox(
            "I confirm that I want to delete all medications.",
            key="confirm_delete_all"
        )

        if st.button(
            "Delete All Medications",
            key="delete_all_button"
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

    st.header(
        "Wellness & Medication Spotlight"
    )

    st.write(
        "Get a random wellness tip or medication spotlight "
        "generated by MediTrack."
    )

    if (
        "wellness_spotlight"
        not in st.session_state
    ):
        with st.spinner(
            "Generating your spotlight..."
        ):
            st.session_state[
                "wellness_spotlight"
            ] = (
                myutils.get_random_wellness_spotlight()
            )

    spotlight = st.session_state[
        "wellness_spotlight"
    ]

    st.subheader(
        spotlight["type"]
    )

    st.info(
        spotlight["content"]
    )

    if st.button(
        "Generate New Spotlight",
        key="generate_new_spotlight"
    ):
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