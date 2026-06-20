import streamlit as st
import pandas as pd

CSV_URL = "https://raw.githubusercontent.com/MFaeli/Bridge_Results_Explorer/main/bridge_fullhalf_stiffness_PRELIMINARY.csv"

@st.cache_data
def load_data():
    return pd.read_csv(CSV_URL)

df = load_data()
df = df[df["status"] == "OK"]

st.set_page_config(page_title="RC Box-Girder Shoring Results")
st.title("RC Box-Girder Deck-Removal Results Explorer")
st.caption("Browse finite-element results for staged deck replacement with falsework")

st.write("Select a bridge configuration to see its computed deflection:")

col1, col2 = st.columns(2)

with col1:
    # 1. span first
    span = st.selectbox("Span (in)", sorted(df["span_in"].unique()))
    # 2. width: only those existing for this span
    width_opts = sorted(df[df["span_in"] == span]["width_in"].unique())
    width = st.selectbox("Width (in)", width_opts)
    # 3. fc: only those existing for this span+width
    fc_opts = sorted(df[(df["span_in"] == span) &
                        (df["width_in"] == width)]["fc_psi"].unique())
    fc = st.selectbox("f'c (psi)", fc_opts)

with col2:
    # 4. depth: ONLY depths that exist for this span+width+fc (the key fix)
    depth_opts = sorted(df[(df["span_in"] == span) &
                           (df["width_in"] == width) &
                           (df["fc_psi"] == fc)]["depth_in"].unique())
    depth = st.selectbox("Box depth (in)", depth_opts)
    # 5. stiffness: only those existing for this exact bridge
    k_opts = sorted(df[(df["span_in"] == span) &
                       (df["width_in"] == width) &
                       (df["fc_psi"] == fc) &
                       (df["depth_in"] == depth)]["k_spring_lbf_per_in"].unique())
    k = st.selectbox("Spring stiffness (lbf/in)", k_opts)
    # 6. scheme
    scheme = st.selectbox("Shoring scheme", ["Full (4 springs)", "Half (2 springs)"])

# now this match will ALWAYS find a row, because every dropdown was filtered
match = df[
    (df["span_in"] == span) &
    (df["depth_in"] == depth) &
    (df["width_in"] == width) &
    (df["fc_psi"] == fc) &
    (df["k_spring_lbf_per_in"] == k)
]

st.divider()

if len(match) == 0:
    st.warning("No result found — please adjust your selection.")
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

        """
    )
