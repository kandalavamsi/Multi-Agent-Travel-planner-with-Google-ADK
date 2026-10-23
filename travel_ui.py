import requests
import streamlit as st

st.set_page_config(page_title="ADK-Powered Travel Planner", page_icon="✈️")

st.title("🌍 ADK-Powered Travel Planner")
st.write("Plan a trip and review estimated flights, stays, and activities.")

origin = st.text_input(
    "Where are you flying from?",
    placeholder="e.g., New York",
)
destination = st.text_input(
    "Destination city and country",
    placeholder="e.g., Delhi, India",
)

date_col1, date_col2 = st.columns(2)
with date_col1:
    start_date = st.date_input("Start date")
with date_col2:
    end_date = st.date_input("End date")

st.subheader("Set your budgets")
budget_col1, budget_col2, budget_col3 = st.columns(3)

with budget_col1:
    flight_budget = st.number_input(
        "Flights per traveler (USD)",
        min_value=0.0,
        step=50.0,
    )
with budget_col2:
    stay_budget = st.number_input(
        "Stays for the whole visit (USD)",
        min_value=0.0,
        step=50.0,
    )
with budget_col3:
    activity_budget = st.number_input(
        "Activities per traveler (USD)",
        min_value=0.0,
        step=25.0,
    )

total_budget = flight_budget + stay_budget + activity_budget
st.caption(f"Combined budget: **${total_budget:,.2f} USD**")

def show_note(result):
    note = result.get("note")
    if note:
        st.caption(note)


def show_plan(data):
    if not isinstance(data, dict):
        raise ValueError("Travel planner response must be a JSON object.")

    flights = data.get("flights", {})
    stays = data.get("stays", {})
    activities = data.get("activities", {})

    for name, result in (
        ("flights", flights),
        ("stays", stays),
        ("activities", activities),
    ):
        if (
            not isinstance(result, dict)
            or not isinstance(result.get("options"), list)
            or not isinstance(result.get("note"), str)
        ):
            raise ValueError(f"Travel planner returned invalid {name} data.")

    st.subheader("✈️ Flight options")
    show_note(flights)
    flight_options = flights.get("options", [])

    if not flight_options:
        st.info("No flight options were returned.")
    else:
        for option in flight_options:
            with st.container(border=True):
                st.markdown(f"### {option.get('airline', 'Flight option')}")
                st.write(f"**Departure:** {option.get('departure', 'Not provided')}")
                st.write(f"**Return:** {option.get('return', 'Not provided')}")
                st.write(f"**Stops:** {option.get('stops', 'Not provided')}")
                price = option.get("estimated_price")
                currency = option.get("currency", "USD")
                if price is not None:
                    st.write(f"**Estimated price:** {currency} {price:,.2f}")

    st.subheader("🏨 Stay options")
    show_note(stays)
    stay_options = stays.get("options", [])

    if not stay_options:
        st.info("No stay options were returned.")
    else:
        for option in stay_options:
            with st.container(border=True):
                st.markdown(f"### {option.get('name', 'Stay option')}")
                st.write(f"**Location:** {option.get('location', 'Not provided')}")
                currency = option.get("currency", "USD")
                nightly_price = option.get("price_per_night")
                total_price = option.get("estimated_total")

                if nightly_price is not None:
                    st.write(
                        f"**Price per night:** {currency} {nightly_price:,.2f}"
                    )
                if total_price is not None:
                    st.write(
                        f"**Estimated stay total:** {currency} {total_price:,.2f}"
                    )

    st.subheader("🗺️ Activities")
    show_note(activities)
    activity_options = activities.get("options", [])

    if not activity_options:
        st.info("No activities were returned.")
    else:
        for option in activity_options:
            with st.container(border=True):
                st.markdown(f"### {option.get('name', 'Activity')}")
                st.write(option.get("description", "No description provided."))
                price = option.get("estimated_price")
                currency = option.get("currency", "USD")
                duration = option.get("duration_hours")

                if price is not None:
                    st.write(f"**Estimated price:** {currency} {price:,.2f}")
                if duration is not None:
                    st.write(f"**Duration:** {duration} hours")


if st.button("Plan My Trip ✨", type="primary"):
    if not origin.strip() or not destination.strip():
        st.warning("Enter both your origin and destination.")
    elif end_date < start_date:
        st.warning("The end date must be on or after the start date.")
    else:
        payload = {
            "origin": origin.strip(),
            "destination": destination.strip(),
            "start_date": str(start_date),
            "end_date": str(end_date),
            "flight_budget": flight_budget,
            "stay_budget": stay_budget,
            "activity_budget": activity_budget,
        }

        try:
            with st.spinner("Gathering your travel suggestions..."):
                response = requests.post(
                    "http://localhost:8000/run",
                    json=payload,
                    timeout=120,
                )
                response.raise_for_status()
                data = response.json()

            show_plan(data)

        except requests.RequestException as exc:
            st.error(f"Could not fetch the travel plan: {exc}")
        except (ValueError, TypeError) as exc:
            st.error(f"The travel planner returned an invalid response: {exc}")