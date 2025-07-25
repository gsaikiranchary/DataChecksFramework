import streamlit as st
import pandas as pd

# Load the uploaded CSV file
@st.cache_data
def load_data(file):
    return pd.read_csv(file)

# Null check
def check_nulls(df, columns):
    return df[columns].isnull().sum()

# Duplicate check
def check_duplicates(df):
    dupdf = df[df.duplicated(keep=False)].groupby(list(df.columns)).size().reset_index(name='dup_count')
    return dupdf



# Data type check
def check_data_types(df, expected_types):
    mismatches = {}
    for col, expected_type in expected_types.items():
        if col in df.columns:
            actual_type = df[col].dropna().map(type).mode()[0].__name__
            if actual_type != expected_type:
                mismatches[col] = f"Expected {expected_type}, Found {actual_type}"
    return mismatches

# Range validation
def check_ranges(df, range_rules):
    violations = {}
    for col, (min_val, max_val) in range_rules.items():
        if col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                invalid = df[(df[col] < min_val) | (df[col] > max_val)]
                if not invalid.empty:
                    violations[col] = invalid[[col]]
            except Exception as e:
                violations[col] = f"Error: {e}"
    return violations

# Streamlit UI
st.title("Data Quality Checks")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    st.write("### Preview of Uploaded Data", df.head())

    st.sidebar.header("Configure Data Quality Checks")

    # Null check columns
    null_check_cols = st.sidebar.multiselect("Select columns for Null Check", df.columns.tolist())

    # Data type check
    st.sidebar.markdown("#### Data Type Validation")
    type_check_cols = st.sidebar.multiselect("Select columns for Type Check", df.columns.tolist())
    expected_types = {}
    for col in type_check_cols:
        expected_types[col] = st.sidebar.selectbox(f"Expected type for {col}", ["int", "float", "str"], key=f"type_{col}")

    # Range check
    st.sidebar.markdown("#### Range Validation")
    range_check_cols = st.sidebar.multiselect("Select columns for Range Check", df.columns.tolist())
    range_rules = {}
    for col in range_check_cols:
        min_val = st.sidebar.number_input(f"Min value for {col}", key=f"min_{col}")
        max_val = st.sidebar.number_input(f"Max value for {col}", key=f"max_{col}")
        range_rules[col] = (min_val, max_val)

    if st.button("Run Data Quality Checks"):
        st.subheader("Null Value Check")
        if null_check_cols:
            nulls = check_nulls(df, null_check_cols)
            st.write(nulls)
        else:
            st.write("No columns selected for null check.")

        st.subheader("Duplicate Records")
        duplicates = check_duplicates(df)
        if not duplicates.empty:
            st.write(duplicates)
        else:
            st.write("No duplicate records found.")

        st.subheader("Data Type Validation")
        if expected_types:
            type_mismatches = check_data_types(df, expected_types)
            if type_mismatches:
                st.write(type_mismatches)
            else:
                st.write("All types match expected values.")
        else:
            st.write("No columns selected for type validation.")

        st.subheader("Range Validation")
        if range_rules:
            range_violations = check_ranges(df, range_rules)
            if range_violations:
                for col, result in range_violations.items():
                    st.write(f"Violations in {col}:", result)
            else:
                st.write("All values within specified ranges.")
        else:
            st.write("No columns selected for range validation.")

 
