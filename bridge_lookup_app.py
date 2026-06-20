import streamlit as st
import pandas as pd

# read the CSV directly from GitHub (raw URL)
CSV_URL = "https://raw.githubusercontent.com/MFaeli/Bridge_Results_Explorer/main/bridge_fullhalf_stiffness_PRELIMINARY.csv"

@st.cache_data
def load_data():
    return pd.read_csv(CSV_URL)

df = load_data()
df = df[df["status"] == "OK"]

st.set_page_config(page_title="RC Box-Girder Shoring Results", page_icon="🌉")
st.title("🌉 RC Box-Girder Deck-Removal Results Explorer")
st.caption("Browse finite-element results for staged deck replacement with falsework")

st.write("Select a bridge configuration to see its computed deflection:")

col1, col2 = st.columns(2)
with col1:
    span = st.selectbox("Span (in)", sorted(df["span_in"].unique()))
    width = st.selectbox("Width (in)", sorted(df["width_in"].unique()))
    fc = st.selectbox("f'c (psi)", sorted(df["fc_psi"].unique()))
with col2:
    depth = st.selectbox("Box depth (in)", sorted(df["depth_in"].unique()))
    k = st.selectbox("Spring stiffness (lbf/in)", sorted(df["k_spring_lbf_per_in"].unique()))
    scheme = st.selectbox("Shoring scheme", ["Full (4 springs)", "Half (2 springs)"])

match = df[
    (df["span_in"] == span) &
    (df["depth_in"] == depth) &
    (df["width_in"] == width) &
    (df["fc_psi"] == fc) &
    (df["k_spring_lbf_per_in"] == k)
]

st.divider()

if len(match) == 0:
    st.warning("No result for this combination. Try a different depth — "
               "depth is tied to span (AASHTO ratio), so not all pairs exist.")
else:
    row = match.iloc[0]
    if scheme.startswith("Full"):
        defl = abs(row["full_defl_in"]); ratio = row["full_defl_ratio"]; nspr = 4
    else:
        defl = abs(row["half_defl_in"]); ratio = row["half_defl_ratio"]; nspr = 2

    dlim = span / 800.0
    st.subheader("Computed Result")
    c1, c2, c3 = st.columns(3)
    c1.metric("Deflection", f"{defl:.4f} in")
    c2.metric("L/800 limit", f"{dlim:.4f} in")
    c3.metric("Demand / Limit", f"{ratio:.2f}")
    st.write(f"**Configuration:** {scheme}, {nspr} springs, "
             f"k = {k:.0e} lbf/in, {int(row['ncell'])} cells")
    st.progress(min(ratio, 1.0))
    if ratio < 1.0:
        st.success(f"✅ WITHIN deflection limit ({ratio*100:.0f}% of allowable)")
    else:
        st.error("⚠️ EXCEEDS deflection limit")

    st.divider()
    st.write("**Full vs Half comparison for this bridge:**")
    cc1, cc2 = st.columns(2)
    cc1.metric("Full (4 springs)", f"{abs(row['full_defl_in']):.4f} in")
    cc2.metric("Half (2 springs)", f"{abs(row['half_defl_in']):.4f} in",
               delta=f"{(abs(row['half_defl_in'])-abs(row['full_defl_in'])):.4f} in more")

st.divider()
with st.expander("ℹ️ About these results"):
    st.markdown(
        """
        Finite-element results from ANSYS analyses of RC box-girder bridges
        undergoing staged full-depth deck replacement with falsework springs.

        - **Full** = 4 falsework springs active | **Half** = 2 springs active
        - Deflection is the maximum after the full staged removal sequence

        **⚠️ Preliminary:** the spring model has a known over-grab limitation, so
        absolute spring/stiffness values should be read as trends, not validated design values.
        """
    )
