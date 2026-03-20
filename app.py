import streamlit as st
from readability import analyze_text

st.set_page_config(page_title="Readability Scorer", layout="wide")

# -----------------------------
# COLOR FUNCTION
# -----------------------------
def get_color(score):
    if score >= 75:
        return "#28a745"  # Green
    elif score >= 50:
        return "#ffc107"  # Yellow
    else:
        return "#dc3545"  # Red

# -----------------------------
# LAYOUT
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.title("📘 Text Readability Scorer")
    st.markdown("### ✨ Analyze your text readability instantly")

    if "text" not in st.session_state:
        st.session_state.text = ""

    uploaded_file = st.file_uploader("Or upload a .txt file")

    if uploaded_file:
        st.session_state.text = uploaded_file.read().decode("utf-8")

    text = st.text_area(
        "Paste your text here",
        value=st.session_state.text,
        height=200
    )

    st.session_state.text = text

    analyze_button = st.button("Analyze", key="analyze_btn")

with col2:
    if analyze_button:
        if text.strip() == "":
            st.warning("Please enter some text.")
        else:
            grade, score, results, suggestions, passive_sentences = analyze_text(text)

            # -----------------------------
            # RESULTS + STATS
            # -----------------------------
            res_col1, res_col2 = st.columns(2)

            with res_col1:
                st.subheader("📊 Overall Result")

                grade_color = get_color(score)
                st.markdown(
                    f"<h3 style='color:{grade_color};'>Grade: {grade}</h3>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"<h3 style='color:{grade_color};'>Score: {score:.2f} / 100</h3>",
                    unsafe_allow_html=True
                )

            with res_col2:
                st.subheader("📈 Text Stats")
                st.write(f"Words: {len(text.split())}")
                st.write(f"Characters: {len(text)}")

            st.divider()

            # -----------------------------
            # BREAKDOWN + SUGGESTIONS
            # -----------------------------
            breakdown_col, suggestions_col = st.columns([1.5, 1])

            with breakdown_col:
                st.subheader("📊 Breakdown")

                for key, (val, msg) in results.items():
                    if isinstance(val, (int, float)):
                        progress_val = max(0, min(int(val), 100))
                        color = get_color(progress_val)

                        # Title with colored score
                        st.markdown(
                            f"**{key}**: <span style='color:{color}; font-weight:bold;'>{val}</span> → {msg}",
                            unsafe_allow_html=True
                        )

                        # Custom colored progress bar
                        st.markdown(
                            f"""
                            <div style="width: 100%; background-color: rgba(255,255,255,0.1); border-radius: 0.5rem; margin-top: 0.5rem; margin-bottom: 1.5rem; height: 0.75rem;">
                                <div style="width: {progress_val}%; background-color: {color}; height: 100%; border-radius: 0.5rem;"></div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        # ✅ CORRECT placement of expander
                        if key == "Passive Voice" and passive_sentences:
                            with st.expander("Show passive sentences"):
                                for s in passive_sentences:
                                    st.markdown(f"- {s}")

                    else:
                        st.write(f"**{key}**: {val} → {msg}")

            with suggestions_col:
                st.subheader("💡 Suggestions")

                if suggestions:
                    for s in suggestions:
                        st.write(f"- {s}")
                else:
                    st.success("No major improvements needed 🎉")