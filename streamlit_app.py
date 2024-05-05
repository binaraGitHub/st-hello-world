import streamlit as st
import json
from datetime import datetime



def load_item_materials():
    try:
        with open("item_materials.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_item_materials(item_materials):
    with open("item_materials.json", "w") as f:
        json.dump(item_materials, f, indent=4)

def calculate_total_used_raw_materials(start_date, end_date, item_materials):
    production_data = load_existing_data()
    total_materials = {}
    for entry in production_data["Data"]:
        entry_date = datetime.strptime(entry["date"], "%Y-%m-%d").date()  # Convert to datetime.date
        if start_date <= entry_date <= end_date:
            for item_data in entry["items"]:
                item = item_data["item type"]
                quantity = item_data["quantity"]
                for material, qty in item_materials[item].items():
                    if material not in total_materials:
                        total_materials[material] = 0
                    total_materials[material] += qty * quantity
    return total_materials






def edit_item_materials():
    st.title("Edit Item Materials")

    # Load item materials
    item_materials = load_item_materials()

    # Display current item materials
    st.header("Current Item Materials")
    st.write(item_materials)

    # Add new item
    st.header("Add New Item")
    new_item_name = st.text_input("Enter Item Name:")
    if st.button("Add Item"):
        item_materials[new_item_name] = {}
        save_item_materials(item_materials)
        st.success("Item added successfully!")

        # Edit item materials
    st.header("Edit Item Materials")
    item_to_edit = st.selectbox("Select Item to Edit:", list(item_materials.keys()))

    # Get all available raw materials
    all_raw_materials = set()
    for materials in item_materials.values():
        all_raw_materials.update(materials.keys())

    # Create a dynamic form to edit quantities for each raw material
    edited_materials = {}
    for material in all_raw_materials:
        quantity = item_materials[item_to_edit].get(material, 0)
        edited_materials[material] = st.number_input(f"Edit Quantity of {material}:", value=quantity)
    if st.button("Save Changes"):
        item_materials[item_to_edit] = edited_materials
        save_item_materials(item_materials)
        st.success("Changes saved successfully!")

    # Delete item
    st.header("Delete Item")
    item_to_delete = st.selectbox("Select Item to Delete:", list(item_materials.keys()))
    if st.button("Delete Item"):
        del item_materials[item_to_delete]
        save_item_materials(item_materials)
        st.success("Item deleted successfully!")
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

def clear_empty_entries():
    # Load production data
    production_data = load_existing_data()

    # Print the original production data
    print("Original production data:", production_data)

    # Filter out entries with all item quantities set to zero
    filtered_data = [entry for entry in production_data["Data"] if any(item_data["quantity"] != 0 for item_data in entry["items"])]

    print("Filtered production data:", filtered_data)

    # Save the filtered production data back to the JSON file
    with open("production_data.json", "w") as f:
        json.dump({"Data": filtered_data}, f)

    st.success("Empty entries cleared successfully!")




def sort_data_by_date(production_data):
    sorted_data = sorted(production_data["Data"], key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"))
    production_data["Data"] = sorted_data
    return production_data

def main():
    st.title("Factory Production and Raw Material Calculator")
    item_materials = load_item_materials()
    # Menu bar
    #menu_options = ["Home", "View Report", "Clear Json", "Set Order JSON", "Edit Item Materials", "User Raw Materials"]
    menu_options = ["Home", "View Report", "Clear Json", "Set Order JSON", "User Raw Materials"]
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
                    st.session_state.quantity_values[item] = st.number_input(f"Enter Quantity of {item} Built", min_value=0, step=1,
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

    elif choice == "Clear Json":
        st.header("Clear Json")
        if st.button("Clear Empty Entries"):
            clear_empty_entries()


    elif choice == "Set Order JSON":
        st.header("Set Order JSON")
        sorted_data = sort_data_by_date(st.session_state.production_data)
        with open("production_data.json", "w") as f:
            json.dump(sorted_data, f)
        st.success("Order of data in JSON file set according to the date.")

    elif choice == "Edit Item Materials":
        edit_item_materials()



    elif choice == "User Raw Materials":
        st.header("User Raw Materials")
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
        if st.button("Calculate"):
            total_materials = calculate_total_used_raw_materials(start_date, end_date, item_materials)
            st.write("Total Used Raw Materials Quantity:")
            for material, quantity in total_materials.items():
                st.write(f"{material}: {quantity}")


if __name__ == "__main__":
    main()
