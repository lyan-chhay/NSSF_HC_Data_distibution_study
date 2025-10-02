





# import os
# import glob
# from collections import Counter
# import streamlit as st
# from PIL import Image

# # ------- CONFIG -------
# BOXPLOT_DIR = os.path.join("Plots", "total_amount", "boxplot")
# DIST_DIR = os.path.join("Plots", "total_amount", "distributions")
# FILTER_ORDER = ["DetailMedical", "Sub-LevelofCare", "Sub-Scheme3"]
# # ----------------------

# st.set_page_config(page_title="Plot viewer", layout="wide")

# def parse_filename_to_kv(fname_no_ext):
#     parts = fname_no_ext.split("_")
#     kv = {}
#     current_k = None
#     current_v = None

#     for part in parts:
#         if "=" in part:
#             if current_k is not None:
#                 kv[current_k] = current_v
#             k, v = part.split("=", 1)
#             current_k = k.strip()
#             current_v = v.strip()
#         else:
#             if current_k is not None:
#                 current_v = current_v + "_" + part
#             else:
#                 continue

#     if current_k is not None:
#         kv[current_k] = current_v

#     return kv

# @st.cache_data(show_spinner=False)
# def scan_plot_files(directory):
#     pattern = os.path.join(directory, "*.png")
#     files = glob.glob(pattern)
#     records = []
#     key_counter = Counter()

#     for fpath in files:
#         fname = os.path.splitext(os.path.basename(fpath))[0]
#         kv = parse_filename_to_kv(fname)
#         for k in kv.keys():
#             key_counter[k] += 1
#         records.append({"path": fpath, "kv": kv, "basename": fname})

#     return records, key_counter

# # scan both dirs
# records_box, key_counter_box = scan_plot_files(BOXPLOT_DIR) if os.path.isdir(BOXPLOT_DIR) else ([], Counter())
# records_dist, key_counter_dist = scan_plot_files(DIST_DIR) if os.path.isdir(DIST_DIR) else ([], Counter())

# # combine keys across both dirs
# all_keys = list((key_counter_box + key_counter_dist).keys())
# chosen_keys = [k for k in FILTER_ORDER if k in all_keys]

# # sidebar filters
# prev_selections = {}
# for key in chosen_keys:
#     candidate_records = records_box + records_dist
#     for pk, sel in prev_selections.items():
#         if sel is None or sel == "(All)":
#             continue
#         candidate_records = [r for r in candidate_records if r["kv"].get(pk) == sel]

#     available_vals = sorted({r["kv"].get(key) for r in candidate_records if r["kv"].get(key) is not None})
#     options = ["(All)"] + available_vals
#     sel = st.sidebar.selectbox(key, options, index=0, key=f"sel_{key}")
#     prev_selections[key] = sel

# # Function to build the canonical filename from selections, dropping the =All parts
# def build_canonical_filename(kv_map, key_order):
#     parts = []
#     for k in key_order:
#         val = kv_map.get(k)
#         if val is None or val == "(All)":
#             continue
#         parts.append(f"{k}={val}")
#     return "_".join(parts) + ".png" if parts else None

# def get_matching_plot(records_all, prev_selections, plots_dir, chosen_keys):
#     matching = []
#     if prev_selections:
#         canonical_fname = build_canonical_filename(prev_selections, chosen_keys)
#         canonical_path = os.path.join(plots_dir, canonical_fname) if canonical_fname else None

#         if canonical_path and os.path.isfile(canonical_path):
#             matching = [{"path": canonical_path}]
#         else:
#             # fallback: find original file with Alls still present
#             candidates = []
#             for r in records_all:
#                 ok = True
#                 for k, sel in prev_selections.items():
#                     if sel == "(All)":
#                         if r["kv"].get(k) != "(All)":
#                             ok = False
#                             break
#                     else:
#                         if r["kv"].get(k) != sel:
#                             ok = False
#                             break
#                 if ok:
#                     candidates.append(r)
#             matching = candidates
#     return matching

# # get matching plots
# matching_box = get_matching_plot(records_box, prev_selections, BOXPLOT_DIR, chosen_keys)
# matching_dist = get_matching_plot(records_dist, prev_selections, DIST_DIR, chosen_keys)

# # display stacked vertically
# if matching_box:
#     st.subheader("Boxplot")
#     for rec in matching_box:
#         st.image(rec["path"] if isinstance(rec, dict) else rec, use_container_width=True)

# if matching_dist:
#     st.subheader("Distribution")
#     for rec in matching_dist:
#         st.image(rec["path"] if isinstance(rec, dict) else rec, use_container_width=True)



import os
import glob
from collections import Counter
import streamlit as st

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

# --- dataset selector ---
dataset_choice = st.sidebar.selectbox("Dataset", DATASETS, index=0)

# paths for this dataset
BOXPLOT_DIR = os.path.join("Plots", dataset_choice, "boxplot")
DIST_DIR = os.path.join("Plots", dataset_choice, "distributions")

# scan both dirs
records_box, key_counter_box = scan_plot_files(BOXPLOT_DIR) if os.path.isdir(BOXPLOT_DIR) else ([], Counter())
records_dist, key_counter_dist = scan_plot_files(DIST_DIR) if os.path.isdir(DIST_DIR) else ([], Counter())
all_keys = list((key_counter_box + key_counter_dist).keys())
chosen_keys = [k for k in FILTER_ORDER if k in all_keys]

# --- reset button ---
if st.sidebar.button("Reset filters"):
    for key in chosen_keys:
        if f"sel_{key}" in st.session_state:
            st.session_state[f"sel_{key}"] = "(All)"



# --- initialize session_state for filters ---
for key in chosen_keys:
    state_key = f"sel_{key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = "(All)"

# --- adaptive selectboxes ---
prev_selections = {}
for i, key in enumerate(chosen_keys):
    # start with all records, then filter by previously selected filters
    candidate_records = records_box + records_dist
    for pk, sel in prev_selections.items():
        if sel == "(All)":
            continue
        candidate_records = [r for r in candidate_records if r["kv"].get(pk) == sel]

    # available options for this filter
    available_vals = sorted({r["kv"].get(key) for r in candidate_records if r["kv"].get(key) is not None})
    options = ["(All)"] + available_vals

    # keep previous selection if still valid
    state_key = f"sel_{key}"
    if st.session_state[state_key] not in options:
        st.session_state[state_key] = "(All)"

    st.session_state[state_key] = st.sidebar.selectbox(
        key, options, index=options.index(st.session_state[state_key])
    )

    prev_selections[key] = st.session_state[state_key]



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
        if canonical_path and os.path.isfile(canonical_path):
            matching = [{"path": canonical_path}]
        else:
            # fallback
            candidates = []
            for r in records_all:
                ok = True
                for k, sel in prev_selections.items():
                    if sel == "(All)":
                        if r["kv"].get(k) != "(All)":
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

# --- get matching plots ---
matching_box = get_matching_plot(records_box, prev_selections, BOXPLOT_DIR, chosen_keys)
matching_dist = get_matching_plot(records_dist, prev_selections, DIST_DIR, chosen_keys)

# --- display vertically ---

if matching_dist:
    st.subheader(f"Distribution - {dataset_choice}")
    for rec in matching_dist:
        st.image(rec["path"] if isinstance(rec, dict) else rec, use_container_width=True)
else:
    st.info("No distribution found for this selection.")


if matching_box:
    st.subheader(f"Boxplot - {dataset_choice}")
    for rec in matching_box:
        st.image(rec["path"] if isinstance(rec, dict) else rec, use_container_width=True)
else:
    st.info("No boxplot found for this selection.")
