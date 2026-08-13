import streamlit as st
import tempfile
from pathlib import Path
import redact_pii

st.set_page_config(
    page_title="PII Redaction Tool 🛡️",
    page_icon="🛡️",
    layout="centered"
)

st.title("🛡️ PII Redaction Tool")
st.markdown(
    "Upload a **PDF document** to automatically detect personally "
    "identifiable information (PII) and download a redacted `.docx` document "
    "with consistent realistic fake replacements (e.g. `Kushal Hegde` → `John Doe`, "
    "`cs.connect@ksh...` → `john.doe@example.com`)."
)

uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    st.info(f"📄 Loaded file: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")
    
    if st.button("🚀 Process & Redact PII", type="primary"):
        with st.spinner("Processing document and redacting sensitive PII..."):
            suffix = Path(uploaded_file.name).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_in:
                tmp_in.write(uploaded_file.getvalue())
                tmp_in_path = Path(tmp_in.name)

            tmp_out_path = tmp_in_path.with_name(f"{tmp_in_path.stem}_redacted.docx")

            try:
                units, reps, cat_counts = redact_pii.pdf_to_docx(tmp_in_path, tmp_out_path)
                unit_label = "pages"

                st.success(f"✅ Successfully processed {units} {unit_label} and performed {reps} redactions!")

                # Display category summary metrics
                st.subheader("📊 Redaction Summary Breakdown")
                cat_names = {
                    "PERSON": "👤 Full Names",
                    "COMPANY": "🏢 Company Names",
                    "EMAIL": "✉️ Email Addresses",
                    "ADDRESS": "🏠 Physical Addresses",
                    "PHONE": "📞 Phone Numbers",
                    "SSN": "🆔 Social Security Numbers",
                    "CREDIT_CARD": "💳 Credit Card Numbers",
                    "DOB": "🎂 Dates of Birth",
                    "IP_ADDRESS": "🌐 IP Addresses",
                }

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Redactions", reps)
                with col2:
                    st.metric(f"Processed {unit_label.capitalize()}", units)

                st.table([{"PII Category": name, "Redactions Made": cat_counts.get(cat, 0)} for cat, name in cat_names.items()])

                # Download button
                with open(tmp_out_path, "rb") as f:
                    redacted_bytes = f.read()

                output_filename = "KSH_PII_Redacted_RHP.docx" if "Red Herring" in uploaded_file.name else f"{Path(uploaded_file.name).stem}_Redacted.docx"
                st.download_button(
                    label="📥 Download Redacted DOCX",
                    data=redacted_bytes,
                    file_name=output_filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary"
                )

            except Exception as err:
                st.error(f"❌ Error processing file: {err}")

            finally:
                # Cleanup temp files
                tmp_in_path.unlink(missing_ok=True)
                tmp_out_path.unlink(missing_ok=True)
