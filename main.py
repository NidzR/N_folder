import streamlit as st
from dotenv import load_dotenv
from fpdf import FPDF
from io import BytesIO
import google.generativeai as genai
import os

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY")) # type: ignore

# Setup Gemini model
model = genai.GenerativeModel("gemini-2.0-flash") # type: ignore

# Clean text to avoid Unicode issues in PDF
def clean_text(text):
    return (
        ''.join(c for c in text if ord(c) < 256)
        .replace("–", "-")
        .replace("’", "'")
        .replace("“", '"')
        .replace("”", '"')
    )

# Generate PDF in memory
def generate_pdf(question, answer):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Math Agent - Solution Report", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.multi_cell(0, 10, f"Question:\n{clean_text(question)}")
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)

    cleaned_text = clean_text(answer)
    for line in cleaned_text.split("\n"):
        pdf.multi_cell(0, 10, line)

    # Output PDF to string, then encode to bytes and wrap in BytesIO
    pdf_output = BytesIO()
    pdf_bytes = pdf.output(dest='S').encode('latin1') # type: ignore
    pdf_output.write(pdf_bytes)
    pdf_output.seek(0)
    return pdf_output


# Ask Gemini to solve the math question
def ask_math_agent(prompt):
    response = model.generate_content(f"You are a helpful math expert. Solve or explain this:\n{prompt}")
    return response.text

# ---------------------- Streamlit UI ----------------------

st.set_page_config("Math Agent", "➗", layout="centered")

st.markdown("""
    <style>
    .reportview-container {
        background: #f5f7fa;
    }
    .stButton > button {
        background-color: #4a90e2;
        color: white;
        border-radius: 8px;
        font-size: 16px;
        padding: 0.5em 1em;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧮 Math Agent")
st.caption("Enter a math question or expression to get a step-by-step solution.")

math_input = st.text_area("Enter your math question:", placeholder="e.g., Solve x^2 + 2x + 1 = 0", height=150)

if st.button("🧠 Solve"):
    if not math_input.strip():
        st.warning("Please enter a math question.")
    else:
        with st.spinner("✍️ Solving with AI..."):
            result = ask_math_agent(math_input)

        st.markdown("### 📘 Solution:")
        st.markdown(result)

        # Download PDF button
        pdf_file = generate_pdf(math_input, result)
        st.download_button(
            label="📄 Download as PDF",
            data=pdf_file,
            file_name="math_solution.pdf",
            mime="application/pdf"
        )

st.markdown("---")
st.markdown("🚀 Made with ❤️ by Muhammad Naeem Warsi")
