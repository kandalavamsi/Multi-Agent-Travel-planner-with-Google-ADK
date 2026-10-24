import requests
import streamlit as st

st.set_page_config(
    page_title="Where to Next? | Travel Planner",
    page_icon="✈️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(ellipse at top left, #eaf4ff 0, transparent 38%),
            linear-gradient(180deg, #f8fbff 0%, #ffffff 45%);
    }

    .block-container {
        max-width: 1120px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 2rem;
        margin-bottom: 1.5rem;
        border-radius: 24px;
        color: white;
        background: linear-gradient(120deg, #123b64, #176b87 60%, #32a6a0);
        box-shadow: 0 16px 40px rgba(18, 59, 100, 0.18);
    }

    .hero-eyebrow {
        margin: 0 0 .5rem;
        color: #c9f2ed;
        font-size: .82rem;
        font-weight: 700;
        letter-spacing: .12em;
        text-transform: uppercase;
    }

    .hero h1 {
        margin: 0;
        color: white;
        font-size: clamp(2rem, 5vw, 3.4rem);
        line-height: 1.1;
    }

    .hero-copy {
        max-width: 650px;
        margin: .8rem 0 0;
        color: #e8f5fb;
        font-size: 1.05rem;
    }

    div[data-testid="stForm"] {
        padding: 1.25rem;
        border: 1px solid #e5edf5;
        border-radius: 20px;
        background: rgba(255, 255, 255, .9);
        box-shadow: 0 8px 28px rgba(24, 53, 80, .06);
    }

    div.stButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        min-height: 3rem;
        border: 0;
        border-radius: 12px;
        color: white;
        background: linear-gradient(100deg, #176b87, #208f91);
        font-weight: 700;
    }

    div.stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {
        color: white;
        border: 0;
        filter: brightness(1.07);
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px;
        border-color: #e5edf5;
        background: white;
    }

    @media (max-width: 700px) {
        .block-container {
            padding: 1rem 1rem 2rem;
        }

        .hero {
            padding: 1.4rem;
            border-radius: 18px;
        }

        .stHorizontalBlock {
            flex-wrap: wrap;
            gap: .75rem;
        }

        .stHorizontalBlock > div {
            flex: 1 1 230px;
            min-width: 0;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="hero">
        <p class="hero-eyebrow">Your next adventure starts here</p>
        <h1>Where to Next? ✈️</h1>
        <p class="hero-copy">
            Tell us where you want to go. We’ll bring your flight, stay,
            and activity suggestions together in one place.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

st.subheader("Build your trip")
st.caption("Set your dates and category budgets. Prices returned by the agents are estimates.")

origin = st.text_input(
    "Flying from",
    placeholder="e.g., Chennai",
)
destination = st.text_input(
    "Destination city",
    placeholder="e.g., Bangkok",
)

with st.form("trip_form"):
    date_col1, date_col2 = st.columns(2)
    with date_col1:
        start_date = st.date_input("Departure date")
    with date_col2:
        end_date = st.date_input("Return date")

    st.markdown("#### Your budgets")
    budget_col1, budget_col2, budget_col3 = st.columns(3)

    with budget_col1:
        flight_budget = st.number_input(
            "Flights per traveler (USD)",
            min_value=0.0,
            step=50.0,
        )
    with budget_col2:
        stay_budget = st.number_input(
            "Stay for the whole visit (USD)",
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
    st.caption(f"Combined category budgets: **${total_budget:,.2f} USD**")

    submitted = st.form_submit_button(
        "✨ Plan my trip",
        use_container_width=True,
    )


def show_note(result):
    note = result.get("note", "")
    if note:
        st.caption(note)


def show_price(label, amount, currency):
    if isinstance(amount, (int, float)) and not isinstance(amount, bool):
        st.write(f"**{label}:** {currency} {amount:,.2f}")


def show_flights(result):
    show_note(result)
    options = result["options"]

    if not options:
        st.info("No flight options were returned. Try adjusting your budget or dates.")
        return

    for option in options:
        with st.container(border=True):
            st.markdown("#### ✈️ Flight option")
            st.text(option.get("airline", "Airline not provided"))
            st.write(f"**Departure:** {option.get('departure', 'Not provided')}")
            st.write(f"**Return:** {option.get('return', 'Not provided')}")
            st.write(f"**Stops:** {option.get('stops', 'Not provided')}")
            show_price(
                "Estimated price",
                option.get("estimated_price"),
                option.get("currency", "USD"),
            )


def show_stays(result):
    show_note(result)
    options = result["options"]

    if not options:
        st.info("No stay options were returned. Try adjusting your dates or budget.")
        return

    for option in options:
        with st.container(border=True):
            st.markdown("#### 🏨 Stay option")
            st.text(option.get("name", "Stay name not provided"))
            st.write(f"**Location:** {option.get('location', 'Not provided')}")
            currency = option.get("currency", "USD")
            show_price("Price per night", option.get("price_per_night"), currency)
            show_price("Estimated stay total", option.get("estimated_total"), currency)


def show_activities(result):
    show_note(result)
    options = result["options"]

    if not options:
        st.info("No activities were returned. Try increasing your activities budget.")
        return

    for option in options:
        with st.container(border=True):
            st.markdown("#### 🗺️ Activity")
            st.text(option.get("name", "Activity name not provided"))
            st.text(option.get("description", "Description not provided"))
            show_price(
                "Estimated price",
                option.get("estimated_price"),
                option.get("currency", "USD"),
            )
            duration = option.get("duration_hours")
            if isinstance(duration, (int, float)) and not isinstance(duration, bool):
                st.write(f"**Duration:** {duration:g} hours")


def show_plan(data):
    if not isinstance(data, dict):
        raise ValueError("Travel planner response must be a JSON object.")

    sections = (
        ("flights", data.get("flights")),
        ("stays", data.get("stays")),
        ("activities", data.get("activities")),
    )

    for name, result in sections:
        if (
            not isinstance(result, dict)
            or not isinstance(result.get("options"), list)
            or not isinstance(result.get("note"), str)
        ):
            raise ValueError(f"Travel planner returned invalid {name} data.")

    st.markdown("---")
    st.subheader("Your trip suggestions")

    flight_tab, stay_tab, activity_tab = st.tabs(
        [
            f"✈️ Flights ({len(data['flights']['options'])})",
            f"🏨 Stays ({len(data['stays']['options'])})",
            f"🗺️ Activities ({len(data['activities']['options'])})",
        ]
    )

    with flight_tab:
        show_flights(data["flights"])

    with stay_tab:
        show_stays(data["stays"])

    with activity_tab:
        show_activities(data["activities"])


if submitted:
    if not origin.strip() or not destination.strip():
        st.warning("Please enter both your origin and destination.")
    elif end_date < start_date:
        st.warning("The return date must be on or after the departure date.")
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
            with st.spinner("✨ Finding ideas for your trip..."):
                response = requests.post(
                    "http://localhost:8000/run",
                    json=payload,
                    timeout=120,
                )
                response.raise_for_status()
                result = response.json()

            show_plan(result)

        except requests.RequestException as exc:
            st.error(f"Could not fetch your trip suggestions: {exc}")
        except (ValueError, TypeError) as exc:
            st.error(f"The planner returned an invalid response: {exc}")