import logging
import json
import azure.functions as func
import re

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="ExtractPatientInfo")
def ExtractPatientInfo(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            "Please pass a valid JSON in the request body",
            status_code=400
        )

    analyze_result = req_body.get('analyzeResult')
    if not analyze_result:
        return func.HttpResponse(
            "Please pass a JSON with 'analyzeResult' in the request body",
            status_code=400
        )
    
    document_content = analyze_result.get('content')
    if not document_content:
        return func.HttpResponse(
            "Please pass 'content' within 'analyzeResult' in the request body",
            status_code=400
        )

    # Extract fields
    name = re.search(r"Name:\s*(.*?)(?:\n|·)", document_content)
    age = re.search(r"Age:\s*(\d+)", document_content)
    gender = re.search(r"Gender:\s*(.*?)(?:\n|·)", document_content)
    date = re.search(r"Date of Examination:\s*(.*?)(?:\n|·)", document_content)

    # Sections: use multi-line match (re.DOTALL) and non-greedy capture
    medical_history = re.search(r"Medical History\s*(.*?)\s*(Notes:|Donor Eligibility|Additional Comments|$)", document_content, re.DOTALL | re.IGNORECASE)
    donor_eligibility = re.search(r"Donor Eligibility.*?\s*(.*?)\s*(Additional Comments|Notes:|$)", document_content, re.DOTALL | re.IGNORECASE)
    
    notes_match = re.search(r"Notes:\s*(.*?)(?:Additional Comments|Donor Eligibility|$)", document_content, re.DOTALL | re.IGNORECASE)
    comments_match = re.search(r"Additional Comments:\s*(.*?)(?:$)", document_content, re.DOTALL | re.IGNORECASE)

    # Construct the JSON response
    response_data = {
        "name": name.group(1).strip() if name else None,
        "age": age.group(1).strip() if age else None,
        "gender": gender.group(1).strip() if gender else None,
        "date": date.group(1).strip() if date else None,
        "medical_history": medical_history.group(1).strip() if medical_history else None,
        "donor_eligibility": donor_eligibility.group(1).strip() if donor_eligibility else None,
        "notes": notes_match.group(1).strip() if notes_match else (
            comments_match.group(1).strip() if comments_match else None
        )
    }

    return func.HttpResponse(
        json.dumps(response_data, indent=2),
        mimetype="application/json",
        status_code=200
    )
