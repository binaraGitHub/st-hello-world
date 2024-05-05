import streamlit as st

# Define the raw material requirements for each item
item_materials = {
    "A": {"X": 1, "Y": 1},
    "B": {"X": 1, "Z": 1},
    "C": {"X": 1, "Z": 2}
}

def calculate_raw_materials(plan):
    total_materials = {}
    for item, quantity in plan.items():
        materials_required = item_materials[item]
        for material, qty in materials_required.items():
            if material not in total_materials:
                total_materials[material] = 0
            total_materials[material] += qty * quantity
    return total_materials

def main():
    st.title("Production Plan Raw Material Calculator")
    st.write("Enter your production plan below:")

    plan = {}
    for item in item_materials:
        quantity = st.number_input(f"Quantity of {item}", min_value=0, step=1)
        plan[item] = quantity

    if st.button("Calculate"):
        total_materials = calculate_raw_materials(plan)
        st.write("Total Required Raw Materials:")
        for material, quantity in total_materials.items():
            st.write(f"{material}: {quantity}")

if __name__ == "__main__":
    main()
