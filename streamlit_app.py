import streamlit as st
import json
from datetime import datetime

# Define the raw material requirements for each item
item_materials = {
    "A": {"X": 1, "Y": 1},
    "B": {"X": 1, "Z": 1},
    "C": {"X": 1, "Z": 2}
}

def load_existing_data():
    try:
        with open("production_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"Data": []}

def generate_summary_report(production_data):
    summary = "### Summary Report\n\n"
    for entry in production_data["Data"]:
        summary += f"#### Date: {entry['date']}\n"
        for item_data in entry["items"]:
            item = item_data["item type"]
            quantity = item_data["quantity"]
            summary += f"- {item}: {quantity}\n"
        summary += "\n"
    return summary

def sort_data_by_date(production_data):
    sorted_data = sorted(production_data["Data"], key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"))
    production_data["Data"] = sorted_data
    return production_data

def main():
    st.title("Factory Production and Raw Material Calculator")

    # Menu bar
    menu_options = ["Home", "View Report", "Set Order JSON"]
    choice = st.sidebar.selectbox("Menu", menu_options)

    if choice == "Home":
        # Initialize session state only if not already initialized
        if "date" not in st.session_state:
            st.session_state.date = None
        if "production_data" not in st.session_state:
            st.session_state.production_data = load_existing_data()
        if "use_existing_data" not in st.session_state:
            st.session_state.use_existing_data = False
        if "quantity_values" not in st.session_state:
            st.session_state.quantity_values = {item: 0 for item in item_materials.keys()}

        # Input production data
        st.header("Enter Daily Production")
        date = st.date_input("Select Date", datetime.today())

        # Simulate button click event to use existing data
        if st.session_state.date != date:  # Check if the date has changed
            st.session_state.date = date  # Update the stored date
            st.session_state.use_existing_data = True  # Simulate button click event

        # Button to populate input fields with existing data
        if st.session_state.use_existing_data:
            existing_data_index = None
            for i, data in enumerate(st.session_state.production_data["Data"]):
                if data["date"] == str(date):
                    existing_data_index = i
                    break
            if existing_data_index is not None:
                existing_data = st.session_state.production_data["Data"][existing_data_index]
                for item_data in existing_data["items"]:
                    item = item_data["item type"]
                    quantity = item_data["quantity"]
                    st.session_state.quantity_values[item] = st.number_input(f"Enter Quantity of {item} Built", min_value=0, step=1,
                                                                             value=quantity,
                                                                             key=f"quantity_{item}")
            else:
                st.session_state.quantity_values = {item: 0 for item in item_materials.keys()}  # Set default values to 0
                for item in item_materials.keys():
                    st.session_state.quantity_values[item] = st.number_input(f"Enter Quantity of {item} Built", min_value=0,
                                                                             step=1,
                                                                             value=st.session_state.quantity_values[item],
                                                                             key=f"quantity_{item}")

        # Save data as JSON
        if st.button("Save Production Data as JSON"):
            # Check if data for the selected date already exists
            date_str = str(date)
            existing_data_index = next((i for i, data in enumerate(st.session_state.production_data["Data"]) if data["date"] == date_str), None)

            if existing_data_index is not None:
                # Update quantities for each item
                st.session_state.production_data["Data"][existing_data_index]["items"] = [{"item type": item, "quantity": st.session_state.quantity_values[item]} for item in item_materials.keys()]
            else:
                # Add new data set
                formatted_data = {
                    "date": date_str,
                    "items": [{"item type": item, "quantity": st.session_state.quantity_values[item]} for item in item_materials.keys()]
                }
                st.session_state.production_data["Data"].append(formatted_data)

            # Save updated data back to JSON file
            with open("production_data.json", "w") as f:
                json.dump(st.session_state.production_data, f)

            st.success("Data saved successfully!")

    elif choice == "View Report":
        st.header("View Report")
        summary_report = generate_summary_report(st.session_state.production_data)
        st.markdown(summary_report)

    elif choice == "Set Order JSON":
        st.header("Set Order JSON")
        sorted_data = sort_data_by_date(st.session_state.production_data)
        with open("production_data.json", "w") as f:
            json.dump(sorted_data, f)
        st.success("Order of data in JSON file set according to the date.")

if __name__ == "__main__":
    main()
