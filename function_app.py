# Forcing redeployment
import logging
import json
import azure.functions as func
import re

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="ExtractPatientInfo", http_auth_level=func.AuthLevel.ANONYMOUS)
def ExtractPatientInfo(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
             "Please pass a valid JSON in the request body",
             status_code=400
        )

    document_content = req_body.get('content')
    if not document_content:
        return func.HttpResponse(
             "Please pass 'content' in the request body",
             status_code=400
        )

    # Use non-greedy regular expressions to extract the data reliably
    # The (.*?) pattern will match as little as possible until the newline character
    name_match = re.search(r"Name:\s*(.*?)(?:\n|·)", document_content)
    age_match = re.search(r"Age:\s*(\d+)", document_content)
    date_match = re.search(r"Date of Examination:\s*(.*?)(?:\n|·)", document_content)
    
    name = name_match.group(1).strip() if name_match else None
    age = age_match.group(1).strip() if age_match else None
    date = date_match.group(1).strip() if date_match else None

    # Construct the JSON response
    response_data = {
        "name": name,
        "age": age,
        "date": date
    }

    return func.HttpResponse(
        json.dumps(response_data),
        mimetype="application/json",
        status_code=200
    )