import json
from google.genai import types
from qna_generator import (
    get_gemini_client,
    parse_json_response,
    PRIMARY_MODEL,
    FALLBACK_MODEL,
)


def _translate_batch(qna_list, target_language):
    if not qna_list:
        return []

    client = get_gemini_client()
    input_json = json.dumps({"qna": qna_list}, ensure_ascii=False)

    prompt = (
        f"You are a professional translator. Translate the following English Question-Answer pairs into natural, accurate {target_language} using Devanagari script.\n"
        "Rules:\n"
        "1. Maintain the exact same number and order of QnA pairs.\n"
        "2. Do not invent, add, or omit information.\n"
        "3. Preserve names and technical terms appropriately.\n"
        "4. Return ONLY valid JSON in this exact structure:\n"
        "{\n"
        '  "qna": [\n'
        f'    {{"question": "{target_language} question", "answer": "{target_language} answer"}}\n'
        "  ]\n"
        "}\n\n"
        f"Input QnA pairs:\n{input_json}"
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
            translated = parse_json_response(response.text)

            if len(translated) != len(qna_list):
                raise ValueError(
                    f"{target_language} translation count mismatch: expected {len(qna_list)}, got {len(translated)}."
                )

            return translated
        except Exception as e:
            last_error = e
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                continue
            break

    raise ValueError(f"Failed to translate to {target_language}: {str(last_error)}")


def translate_to_hindi(qna_list):
    return _translate_batch(qna_list, "Hindi")


def translate_to_marathi(qna_list):
    return _translate_batch(qna_list, "Marathi")
