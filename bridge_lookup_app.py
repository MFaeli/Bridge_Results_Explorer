import streamlit as st
import pandas as pd

CSV_URL = "https://raw.githubusercontent.com/MFaeli/Bridge_Results_Explorer/main/bridge_fullhalf_stiffness_PRELIMINARY.csv"

@st.cache_data
def load_data():
    return pd.read_csv(CSV_URL)

df = load_data()
df = df[df["status"] == "OK"]

st.set_page_config(page_title="RC Box-Girder Shoring Results", layout="wide")

BLANK = "— select —"

with st.sidebar:
    st.header("Bridge Configuration")

    span_sel = st.selectbox("Span (in)",
        [BLANK] + sorted(df["span_in"].unique().tolist()))

    if span_sel == BLANK:
        width_sel = st.selectbox("Width (in)", [BLANK], disabled=True)
        fc_sel = st.selectbox("f'c (psi)", [BLANK], disabled=True)
        depth_sel = st.selectbox("Box depth (in)", [BLANK], disabled=True)
        k_sel = st.selectbox("Spring stiffness (lbf/in)", [BLANK], disabled=True)
        scheme_sel = st.selectbox("Shoring scheme", [BLANK], disabled=True)
    else:
        span = float(span_sel)
        width_opts = sorted(df[df["span_in"] == span]["width_in"].unique().tolist())
        width_sel = st.selectbox("Width (in)", [BLANK] + width_opts)

        if width_sel == BLANK:
            fc_sel = st.selectbox("f'c (psi)", [BLANK], disabled=True)
            depth_sel = st.selectbox("Box depth (in)", [BLANK], disabled=True)
            k_sel = st.selectbox("Spring stiffness (lbf/in)", [BLANK], disabled=True)
            scheme_sel = st.selectbox("Shoring scheme", [BLANK], disabled=True)
        else:
            width = float(width_sel)
            fc_opts = sorted(df[(df["span_in"] == span) &
                                (df["width_in"] == width)]["fc_psi"].unique().tolist())
            fc_sel = st.selectbox("f'c (psi)", [BLANK] + fc_opts)

            if fc_sel == BLANK:
                depth_sel = st.selectbox("Box depth (in)", [BLANK], disabled=True)
                k_sel = st.selectbox("Spring stiffness (lbf/in)", [BLANK], disabled=True)
                scheme_sel = st.selectbox("Shoring scheme", [BLANK], disabled=True)
            else:
                fc = float(fc_sel)
                depth_opts = sorted(df[(df["span_in"] == span) &
                                       (df["width_in"] == width) &
                                       (df["fc_psi"] == fc)]["depth_in"].unique().tolist())
                depth_sel = st.selectbox("Box depth (in)", [BLANK] + depth_opts)

                if depth_sel == BLANK:
                    k_sel = st.selectbox("Spring stiffness (lbf/in)", [BLANK], disabled=True)
                    scheme_sel = st.selectbox("Shoring scheme", [BLANK], disabled=True)
                else:
                    depth = float(depth_sel)
                    k_opts = sorted(df[(df["span_in"] == span) &
                                       (df["width_in"] == width) &
                                       (df["fc_psi"] == fc) &
                                       (df["depth_in"] == depth)]["k_spring_lbf_per_in"].unique().tolist())
                    k_sel = st.selectbox("Spring stiffness (lbf/in)", [BLANK] + [f"{x:.0e}" for x in k_opts])

                    if k_sel == BLANK:
                        scheme_sel = st.selectbox("Shoring scheme", [BLANK], disabled=True)
                    else:
                        k = float(k_sel)
                        scheme_sel = st.selectbox("Shoring scheme",
                            [BLANK, "Full (4 springs)", "Half (2 springs)"])

    # the Show Result button (always visible at the bottom of the sidebar)
    st.write("")
    show = st.button("Show Result", type="primary", use_container_width=True)

# ---- MAIN AREA ----
st.title("RC Box-Girder Deck-Removal Results Explorer")

all_selected = (span_sel != BLANK and width_sel != BLANK and fc_sel != BLANK
                and depth_sel != BLANK and k_sel != BLANK and scheme_sel != BLANK)

if not show:
    st.info("Select all bridge configuration options in the left panel, then click **Show Result**.")
elif not all_selected:
    st.warning("Please complete all selections before clicking Show Result.")
else:
    match = df[
        (df["span_in"] == span) &
        (df["depth_in"] == depth) &
        (df["width_in"] == width) &
        (df["fc_psi"] == fc) &
        (df["k_spring_lbf_per_in"] == k)
    ]

    if len(match) == 0:
        st.warning("No result found — please adjust your selection.")
    else:
        row = match.iloc[0]
        if scheme_sel.startswith("Full"):
            defl = abs(row["full_defl_in"]); ratio = row["full_defl_ratio"]; nspr = 4
        else:
            defl = abs(row["half_defl_in"]); ratio = row["half_defl_ratio"]; nspr = 2

        dlim = span / 800.0

        c1, c2, c3 = st.columns(3)
        c1.metric("Deflection", f"{defl:.4f} in")
        c2.metric("L/800 limit", f"{dlim:.4f} in")
        c3.metric("Demand / Limit", f"{ratio:.2f}")

        st.write(f"**Configuration:** {scheme_sel}, {nspr} springs, "
                 f"k = {k:.0e} lbf/in, {int(row['ncell'])} cells")
        st.progress(min(ratio, 1.0))
        if ratio < 1.0:
            st.success(f"WITHIN deflection limit ({ratio*100:.0f}% of allowable)")
        else:
            st.error("EXCEEDS deflection limit")

        st.divider()
        st.write("**Full vs Half comparison for this bridge:**")
        cc1, cc2 = st.columns(2)
        cc1.metric("Full (4 springs)", f"{abs(row['full_defl_in']):.4f} in")
        cc2.metric("Half (2 springs)", f"{abs(row['half_defl_in']):.4f} in",
                   delta=f"{(abs(row['half_defl_in'])-abs(row['full_defl_in'])):.4f} in more")
