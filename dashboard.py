

import os
import glob
from collections import Counter
import streamlit as st
from PIL import Image

# ------- CONFIG -------
DATASETS = ["total_amount", "ffs_amount", "CB_amount", "medical_stay_day", "sickleave_day"]
FILTER_ORDER = ["DetailMedical", "Sub-LevelofCare", "Sub-Scheme3"]
# ----------------------

st.set_page_config(page_title="Plot viewer", layout="wide")

def parse_filename_to_kv(fname_no_ext):
    parts = fname_no_ext.split("_")
    kv = {}
    current_k = None
    current_v = None
    for part in parts:
        if "=" in part:
            if current_k is not None:
                kv[current_k] = current_v
            k, v = part.split("=", 1)
            current_k = k.strip()
            current_v = v.strip()
        else:
            if current_k is not None:
                current_v = current_v + "_" + part
    if current_k is not None:
        kv[current_k] = current_v
    return kv

@st.cache_data(show_spinner=False)
def scan_plot_files(directory):
    pattern = os.path.join(directory, "*.png")
    files = glob.glob(pattern)
    records = []
    key_counter = Counter()
    for fpath in files:
        fname = os.path.splitext(os.path.basename(fpath))[0]
        kv = parse_filename_to_kv(fname)
        for k in kv.keys():
            key_counter[k] += 1
        records.append({"path": fpath, "kv": kv, "basename": fname})
    return records, key_counter

# --- Filter section with title ---
st.sidebar.markdown("### Data Selection")
dataset_choice = st.sidebar.selectbox(
    "Select dataset",  # Provide a proper label
    DATASETS, 
    index=0, 
    label_visibility="collapsed"  # Hide the label since we have the header
)

# paths for this dataset
BOXPLOT_DIR = os.path.join("Plots", dataset_choice, "boxplot")
DIST_DIR = os.path.join("Plots", dataset_choice, "distributions")

# scan both dirs
records_box, key_counter_box = scan_plot_files(BOXPLOT_DIR) if os.path.isdir(BOXPLOT_DIR) else ([], Counter())
records_dist, key_counter_dist = scan_plot_files(DIST_DIR) if os.path.isdir(DIST_DIR) else ([], Counter())
all_records = records_box + records_dist

# Get all keys from the records
all_keys = list((key_counter_box + key_counter_dist).keys())
chosen_keys = [k for k in FILTER_ORDER if k in all_keys]


# --- Filter section with title ---
st.sidebar.markdown("### Filter")


# Initialize session state for filters if not exists
for key in chosen_keys:
    if f"sel_{key}" not in st.session_state:
        st.session_state[f"sel_{key}"] = "(All)"

# Add a reset flag to session state
if "reset_flag" not in st.session_state:
    st.session_state.reset_flag = False

# --- reset button ---
if st.sidebar.button("Reset filters"):
    for key in chosen_keys:
        st.session_state[f"sel_{key}"] = "(All)"
    st.session_state.reset_flag = True
    st.rerun()

# If reset was just performed, clear the flag
if st.session_state.reset_flag:
    st.session_state.reset_flag = False

# Function to get available values for a filter based on current selections
def get_available_values(records, current_key, current_selections):
    # Filter records based on current selections (excluding the current key)
    filtered_records = records.copy()
    
    for key, value in current_selections.items():
        if key != current_key and value != "(All)":
            filtered_records = [r for r in filtered_records if r["kv"].get(key) == value]
    
    # Get available values for the current key
    available_values = sorted({r["kv"].get(current_key) for r in filtered_records if r["kv"].get(current_key) is not None})
    return available_values



# Build current selections from session state - create a fresh copy
current_selections = {}
for key in chosen_keys:
    current_selections[key] = st.session_state[f"sel_{key}"]

# Create dynamic filters
for i, key in enumerate(chosen_keys):
    # Get available values for this filter based on current selections of other filters
    available_vals = get_available_values(all_records, key, current_selections)
    options = ["(All)"] + available_vals
    
    # If current selection is not in available options, reset it to "(All)"
    if st.session_state[f"sel_{key}"] not in options:
        st.session_state[f"sel_{key}"] = "(All)"
    
    # Create the selectbox
    selection = st.sidebar.selectbox(
        key, 
        options, 
        index=options.index(st.session_state[f"sel_{key}"]),
        key=f"sel_{key}"
    )
    
    # Only update if the selection actually changed
    if selection != st.session_state[f"sel_{key}"]:
        st.session_state[f"sel_{key}"] = selection
    
    # Update current_selections for the next iteration
    current_selections[key] = st.session_state[f"sel_{key}"]

# Use the current selections from session state for the rest of the logic
prev_selections = {key: st.session_state[f"sel_{key}"] for key in chosen_keys}

# --- filename builder ---
def build_canonical_filename(kv_map, key_order):
    parts = []
    for k in key_order:
        val = kv_map.get(k)
        if val is None or val == "(All)":
            continue
        parts.append(f"{k}={val}")
    return "_".join(parts) + ".png" if parts else None

def get_matching_plot(records_all, prev_selections, plots_dir, chosen_keys):
    matching = []
    if prev_selections:
        canonical_fname = build_canonical_filename(prev_selections, chosen_keys)
        canonical_path = os.path.join(plots_dir, canonical_fname) if canonical_fname else None
        
        # Check if canonical path exists
        if canonical_path and os.path.isfile(canonical_path):
            matching = [{"path": canonical_path}]
        else:
            # fallback: filter records based on selections
            candidates = []
            for r in records_all:
                ok = True
                for k, sel in prev_selections.items():
                    if sel == "(All)":
                        # For "(All)", we want records that have any value for this key (not None)
                        if r["kv"].get(k) is None:
                            ok = False
                            break
                    else:
                        if r["kv"].get(k) != sel:
                            ok = False
                            break
                if ok:
                    candidates.append(r)
            matching = candidates
    return matching

# Function to safely display image with error handling
def safe_display_image(image_path, alt_text="Plot"):
    try:
        # Check if file exists
        if not os.path.isfile(image_path):
            st.error(f"Image file not found: {os.path.basename(image_path)}")
            return False
            
        # Try to open and display the image
        image = Image.open(image_path)
        st.image(image, width='stretch', caption=os.path.basename(image_path))
        return True
        
    except Exception as e:
        st.error(f"Error loading image {os.path.basename(image_path)}: {str(e)}")
        return False

# --- get matching plots ---
matching_box = get_matching_plot(records_box, prev_selections, BOXPLOT_DIR, chosen_keys)
matching_dist = get_matching_plot(records_dist, prev_selections, DIST_DIR, chosen_keys)

# --- display vertically ---
if matching_dist:
    st.subheader(f"Distribution - {dataset_choice}")
    display_count = 0
    for rec in matching_dist:
        image_path = rec["path"] if isinstance(rec, dict) else rec
        if safe_display_image(image_path):
            display_count += 1
    
    if display_count == 0:
        st.info("No distribution images could be loaded for this selection.")
else:
    st.info("No distribution found for this selection.")

if matching_box:
    st.subheader(f"Boxplot - {dataset_choice}")
    display_count = 0
    for rec in matching_box:
        image_path = rec["path"] if isinstance(rec, dict) else rec
        if safe_display_image(image_path):
            display_count += 1
    
    if display_count == 0:
        st.info("No boxplot images could be loaded for this selection.")
else:
    st.info("No boxplot found for this selection.")

