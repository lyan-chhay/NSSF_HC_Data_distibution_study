# import os
# import streamlit as st

# # Base directories
# BOXPLOT_DIR = "results/total_amount/boxplot"
# DIST_DIR = "results/total_amount/distributions"

# # --- Helper functions ---
# def collect_files(base_dir):
#     files = []
#     for root, _, fns in os.walk(base_dir):
#         for f in fns:
#             if f.endswith(".png"):
#                 rel_path = os.path.relpath(os.path.join(root, f), base_dir)
#                 parts = rel_path.split(os.sep)
#                 files.append(parts)
#     return files

# def build_index(files, base_dir):
#     data = []
#     for parts in files:
#         if len(parts) == 3:  # Sub-Medical/Sub-Level/Sub-Scheme.png
#             sub_medical = parts[0]
#             sub_level = parts[1]
#             sub_scheme = parts[2].replace(".png", "")
#             data.append({
#                 "Sub-Medical": sub_medical,
#                 "Sub-Level": sub_level,
#                 "Sub-Scheme": sub_scheme,
#                 "path": os.path.join(base_dir, *parts)
#             })
#     return data

# def resolve_path(data, medical, level, scheme, base_dir):
#     if medical is None:
#         return None  # nothing to load
#     if level == "None" and scheme == "None":
#         # Top-level plot
#         path = os.path.join(base_dir, medical + ".png")
#         return path if os.path.exists(path) else None
#     elif scheme == "None":
#         # Sub-Level only
#         path = os.path.join(base_dir, medical, f"{level}.png")
#         return path if os.path.exists(path) else None
#     else:
#         # Full drill-down
#         match = next((d for d in data if
#                       d["Sub-Medical"] == medical and
#                       d["Sub-Level"] == level and
#                       d["Sub-Scheme"] == scheme), None)
#         return match["path"] if match else None

# # --- Load data ---
# boxplot_data = build_index(collect_files(BOXPLOT_DIR), BOXPLOT_DIR)
# dist_data = build_index(collect_files(DIST_DIR), DIST_DIR)

# # --- Streamlit config ---
# st.set_page_config(layout="wide")
# st.sidebar.title("Filters")

# # --- Session state initialization ---
# for key in ["selected_medical", "selected_level", "selected_scheme"]:
#     if key not in st.session_state:
#         if key == "selected_level" or key == "selected_scheme":
#             st.session_state[key] = "None"  # bottom filters default to "None"
#         else:
#             st.session_state[key] = None

# # --- Prepare filter options ---
# sub_medicals = sorted(set(d["Sub-Medical"] for d in boxplot_data))

# # --- Reset button ---
# if st.sidebar.button("Reset filters"):
#     st.session_state.selected_medical = sub_medicals[0]  # reset first medical
#     st.session_state.selected_level = "None"
#     st.session_state.selected_scheme = "None"

# # --- Filter widgets bound to session_state ---
# selected_medical = st.sidebar.selectbox(
#     "Sub-Medical",
#     options=sub_medicals,
#     key="selected_medical"
# )

# filtered_level = [d for d in boxplot_data if d["Sub-Medical"] == selected_medical]
# level_options = ["None"] + sorted(set(d["Sub-Level"] for d in filtered_level))
# selected_level = st.sidebar.selectbox(
#     "Sub-Level of Care",
#     options=level_options,
#     key="selected_level"
# )

# if selected_level != "None":
#     filtered_scheme = [d for d in filtered_level if d["Sub-Level"] == selected_level]
#     scheme_options = ["None"] + sorted(set(d["Sub-Scheme"] for d in filtered_scheme))
# else:
#     scheme_options = ["None"]

# selected_scheme = st.sidebar.selectbox(
#     "Sub-Scheme 3",
#     options=scheme_options,
#     key="selected_scheme"
# )

# # --- Resolve image paths safely ---
# dist_path = resolve_path(dist_data, selected_medical, selected_level, selected_scheme, DIST_DIR)
# boxplot_path = resolve_path(boxplot_data, selected_medical, selected_level, selected_scheme, BOXPLOT_DIR)

# # --- Display ---
# st.markdown(f"### {selected_medical} | {selected_level} | {selected_scheme}")

# # Distribution on top
# if dist_path:
#     st.image(dist_path, caption="Distribution", use_container_width=True)
# else:
#     st.warning("No distribution plot available for this selection.")

# # Boxplot below
# if boxplot_path:
#     st.image(boxplot_path, caption="Boxplot", use_container_width=True)
# else:
#     st.warning("No boxplot available for this selection.")


import os
import streamlit as st

# --- Base directories for both options ---
DATA_OPTIONS = {
    "Total Amount": "results/total_amount",
    "FFS Amount": "results/ffs_amount"
}

# --- Helper functions ---
def collect_files(base_dir):
    files = []
    for root, _, fns in os.walk(base_dir):
        for f in fns:
            if f.endswith(".png"):
                rel_path = os.path.relpath(os.path.join(root, f), base_dir)
                parts = rel_path.split(os.sep)
                files.append(parts)
    return files

def build_index(files, base_dir):
    data = []
    for parts in files:
        if len(parts) == 3:  # Sub-Medical/Sub-Level/Sub-Scheme.png
            sub_medical = parts[0]
            sub_level = parts[1]
            sub_scheme = parts[2].replace(".png", "")
            data.append({
                "Sub-Medical": sub_medical,
                "Sub-Level": sub_level,
                "Sub-Scheme": sub_scheme,
                "path": os.path.join(base_dir, *parts)
            })
    return data

def resolve_path(data, medical, level, scheme, base_dir):
    if medical is None:
        return None
    if level == "None" and scheme == "None":
        path = os.path.join(base_dir, medical + ".png")
        return path if os.path.exists(path) else None
    elif scheme == "None":
        path = os.path.join(base_dir, medical, f"{level}.png")
        return path if os.path.exists(path) else None
    else:
        match = next((d for d in data if
                      d["Sub-Medical"] == medical and
                      d["Sub-Level"] == level and
                      d["Sub-Scheme"] == scheme), None)
        return match["path"] if match else None

# --- Streamlit config ---
st.set_page_config(layout="wide")
st.sidebar.title("Data Selection")

# --- Top-level option: dataset selection ---
selected_dataset = st.sidebar.selectbox("Select Dataset", list(DATA_OPTIONS.keys()))


st.sidebar.title("Filters")
# --- Base directories for selected dataset ---
BASE_DIR = DATA_OPTIONS[selected_dataset]
BOXPLOT_DIR = os.path.join(BASE_DIR, "boxplot")
DIST_DIR = os.path.join(BASE_DIR, "distributions")

# --- Load data ---
boxplot_data = build_index(collect_files(BOXPLOT_DIR), BOXPLOT_DIR)
dist_data = build_index(collect_files(DIST_DIR), DIST_DIR)

# --- Session state initialization ---
for key in ["selected_medical", "selected_level", "selected_scheme"]:
    if key not in st.session_state:
        if key in ["selected_level", "selected_scheme"]:
            st.session_state[key] = "None"
        else:
            st.session_state[key] = None

# --- Prepare filter options ---
sub_medicals = sorted(set(d["Sub-Medical"] for d in boxplot_data))

# --- Reset button ---
if st.sidebar.button("Reset filters"):
    st.session_state.selected_medical = sub_medicals[0]
    st.session_state.selected_level = "None"
    st.session_state.selected_scheme = "None"

# --- Filter widgets bound to session_state ---
selected_medical = st.sidebar.selectbox(
    "Sub-Medical",
    options=sub_medicals,
    key="selected_medical"
)

filtered_level = [d for d in boxplot_data if d["Sub-Medical"] == selected_medical]
level_options = ["None"] + sorted(set(d["Sub-Level"] for d in filtered_level))
selected_level = st.sidebar.selectbox(
    "Sub-Level of Care",
    options=level_options,
    key="selected_level"
)

if selected_level != "None":
    filtered_scheme = [d for d in filtered_level if d["Sub-Level"] == selected_level]
    scheme_options = ["None"] + sorted(set(d["Sub-Scheme"] for d in filtered_scheme))
else:
    scheme_options = ["None"]

selected_scheme = st.sidebar.selectbox(
    "Sub-Scheme 3",
    options=scheme_options,
    key="selected_scheme"
)

# --- Resolve image paths safely ---
dist_path = resolve_path(dist_data, selected_medical, selected_level, selected_scheme, DIST_DIR)
boxplot_path = resolve_path(boxplot_data, selected_medical, selected_level, selected_scheme, BOXPLOT_DIR)

# --- Display ---
st.markdown(f"### Dataset: {selected_dataset} | {selected_medical} | {selected_level} | {selected_scheme}")

# Distribution on top
if dist_path:
    st.image(dist_path, caption="Distribution", use_container_width=True)
else:
    st.warning("No distribution plot available for this selection.")

# Boxplot below
if boxplot_path:
    st.image(boxplot_path, caption="Boxplot", use_container_width=True)
else:
    st.warning("No boxplot available for this selection.")

