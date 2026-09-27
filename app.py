import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from document_processor import extract_text
from qna_generator import generate_qna
from translator import translate_to_hindi, translate_to_marathi
from excel_generator import generate_excel_bytes, save_excel_file

load_dotenv()

st.set_page_config(
    page_title="Multilingual QnA Generation System",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    header { visibility: hidden !important; display: none !important; }
    #MainMenu { visibility: hidden !important; display: none !important; }
    .stDeployButton { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    footer { visibility: hidden !important; display: none !important; }
    .block-container { max-width: 800px !important; padding-top: 2rem !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


def main():
    st.title("Multilingual Question-Answer Generation System")
    st.write("Upload a PDF, DOCX, or TXT document and generate aligned QnA pairs in English, Hindi, and Marathi.")

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or "your_" in api_key.lower():
        st.warning("Please configure your GEMINI_API_KEY in the .env file.")

    uploaded_file = st.file_uploader(
        "Upload Document",
        type=["pdf", "docx", "txt"],
    )

    num_questions = st.selectbox(
        "Select Number of Questions",
        options=[5, 10, 15, 20, 25, 30, 40, 50],
        index=1,
    )

    if "english_qna" not in st.session_state:
        st.session_state.english_qna = None
        st.session_state.hindi_qna = None
        st.session_state.marathi_qna = None
        st.session_state.excel_bytes = None

    if st.button("Generate QnA", type="primary", use_container_width=True):
        if not uploaded_file:
            st.error("Please upload a document (.pdf, .docx, or .txt) first.")
            return

        if not api_key or "your_" in api_key.lower():
            st.error("GEMINI_API_KEY is missing in .env file.")
            return

        status = st.empty()

        try:
            status.info("Extracting document text...")
            text = extract_text(uploaded_file, uploaded_file.name)

            status.info("Generating English QnAs...")
            english_qna = generate_qna(text, num_questions=num_questions)

            status.info("Translating to Hindi...")
            hindi_qna = translate_to_hindi(english_qna)

            status.info("Translating to Marathi...")
            marathi_qna = translate_to_marathi(english_qna)

            status.info("Creating Excel file...")
            excel_bytes = generate_excel_bytes(english_qna, hindi_qna, marathi_qna)
            save_excel_file(english_qna, hindi_qna, marathi_qna, "QnA.xlsx")

            st.session_state.english_qna = english_qna
            st.session_state.hindi_qna = hindi_qna
            st.session_state.marathi_qna = marathi_qna
            st.session_state.excel_bytes = excel_bytes

            status.success("QnA generation completed.")

        except ValueError as ve:
            status.empty()
            st.error(str(ve))
            return
        except Exception as e:
            status.empty()
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                st.warning("Rate limit reached. Please wait a few seconds and try again.")
            else:
                st.error(f"Error during processing: {str(e)}")
            return

    if st.session_state.english_qna and st.session_state.excel_bytes:
        st.divider()
        st.subheader("Generated QnA Preview")

        tab_en, tab_hi, tab_mr = st.tabs(["English", "Hindi", "Marathi"])

        with tab_en:
            df_en = pd.DataFrame(st.session_state.english_qna)
            df_en.columns = ["Questions", "Answers"]
            df_en.index = df_en.index + 1
            st.dataframe(df_en, use_container_width=True)

        with tab_hi:
            df_hi = pd.DataFrame(st.session_state.hindi_qna)
            df_hi.columns = ["Questions", "Answers"]
            df_hi.index = df_hi.index + 1
            st.dataframe(df_hi, use_container_width=True)

        with tab_mr:
            df_mr = pd.DataFrame(st.session_state.marathi_qna)
            df_mr.columns = ["Questions", "Answers"]
            df_mr.index = df_mr.index + 1
            st.dataframe(df_mr, use_container_width=True)

        st.download_button(
            label="Download QnA.xlsx",
            data=st.session_state.excel_bytes,
            file_name="QnA.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
