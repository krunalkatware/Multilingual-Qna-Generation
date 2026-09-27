import os
import re
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

PRIMARY_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")
FALLBACK_MODEL = "gemini-3.8-flash"


def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or "your_" in api_key.lower():
        raise ValueError("GEMINI_API_KEY is not configured in .env file.")
    return genai.Client(api_key=api_key)


def parse_json_response(raw_text):
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start : end + 1]

    data = json.loads(text)
    qna_list = data.get("qna", [])

    valid_qna = []
    for item in qna_list:
        q = str(item.get("question", "")).strip()
        a = str(item.get("answer", "")).strip()
        if q and a:
            valid_qna.append({"question": q, "answer": a})

    if not valid_qna:
        raise ValueError("No valid QnA pairs found in Gemini response.")

    return valid_qna


def remove_duplicate_questions(qna_list):
    seen = set()
    unique_qnas = []

    for item in qna_list:
        q_norm = re.sub(r"[^\w\s]", "", item["question"].lower()).strip()
        if q_norm not in seen:
            seen.add(q_norm)
            unique_qnas.append(item)

    return unique_qnas


def generate_qna(document_text, num_questions=10):
    if not document_text or not document_text.strip():
        raise ValueError("Document text is empty.")

    client = get_gemini_client()

    prompt = (
        "You are an intelligent Question-Answer generation system.\n"
        "The document may be in English, Hindi, Marathi, or mixed languages.\n"
        "Generate meaningful Question-Answer pairs based ONLY on the provided document.\n"
        "Do not invent facts or use outside knowledge.\n"
        "Return the questions and answers in English as the canonical set.\n"
        f"Generate approximately {num_questions} QnA pairs.\n\n"
        "Return valid JSON in this exact format:\n"
        "{\n"
        '  "qna": [\n'
        '    {"question": "English question", "answer": "English answer"}\n'
        "  ]\n"
        "}\n\n"
        f"DOCUMENT:\n{document_text}"
    )

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.2,
    )

    models_to_try = [PRIMARY_MODEL, FALLBACK_MODEL] if PRIMARY_MODEL != FALLBACK_MODEL else [PRIMARY_MODEL]
    last_error = None

    for model in models_to_try:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )
            raw_qnas = parse_json_response(response.text)
            deduped = remove_duplicate_questions(raw_qnas)
            return deduped[:num_questions]
        except Exception as e:
            last_error = e
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                continue
            break

    raise ValueError(f"Failed to generate QnA: {str(last_error)}")
