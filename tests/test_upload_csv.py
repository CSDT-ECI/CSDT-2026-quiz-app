"""Tests for CSV/JSON upload endpoint in app/api/quiz.py."""
import io
import json


CSV_VALID = (
    "question,a_option,b_option,c_option,d_option,answer\n"
    "What is 2+2?,3,4,5,6,b_option\n"
    "Sky color?,red,blue,green,yellow,b_option\n"
)

CSV_MISSING_ANSWER = (
    "question,a_option,b_option\n"
    "What is 2+2?,3,4\n"
)

CSV_MISSING_QUESTION = (
    "a_option,b_option,answer\n"
    "3,4,b_option\n"
)

JSON_VALID = json.dumps([
    {
        "question": "What is 1+1?",
        "a_option": "1",
        "b_option": "2",
        "c_option": "3",
        "answer": "b_option",
    }
])

JSON_MISSING_FIELDS = json.dumps([
    {"question": "Incomplete question"}
])

JSON_INVALID_TEXT = "this is not valid json {"


def _login(client, username="csvuser"):
    client.post(
        "/api/add-account",
        data=json.dumps({
            "full_name": "CSV User",
            "username": username,
            "password": "secret123",
            "password_confirmation": "secret123",
            "email": f"{username}@example.com",
        }),
        content_type="application/json",
    )
    client.post(
        "/api/login",
        data=json.dumps({"username": username, "password": "secret123"}),
        content_type="application/json",
    )


def test_upload_csv_valid_file(client):
    """Valid CSV upload should return success with a quiz code."""
    _login(client)
    data = {
        "csv": (io.BytesIO(CSV_VALID.encode("utf-8")), "quiz.csv"),
        "quiz_title": "CSV Quiz",
    }
    response = client.post(
        "/api/quiz/uploadCsv",
        data=data,
        content_type="multipart/form-data",
    )
    result = response.get_json()
    assert result["status"] == "success"
    assert "code" in result


def test_upload_csv_missing_answer_field(client):
    """CSV missing 'answer' column should return failed."""
    _login(client, "csvuser2")
    data = {
        "csv": (io.BytesIO(CSV_MISSING_ANSWER.encode("utf-8")), "bad.csv"),
    }
    response = client.post(
        "/api/quiz/uploadCsv",
        data=data,
        content_type="multipart/form-data",
    )
    result = response.get_json()
    assert result["status"] == "failed"


def test_upload_csv_missing_question_field(client):
    """CSV missing 'question' column should return failed."""
    _login(client, "csvuser3")
    data = {
        "csv": (io.BytesIO(CSV_MISSING_QUESTION.encode("utf-8")), "bad.csv"),
    }
    response = client.post(
        "/api/quiz/uploadCsv",
        data=data,
        content_type="multipart/form-data",
    )
    result = response.get_json()
    assert result["status"] == "failed"


def test_upload_no_file(client):
    """Upload with no file attached should return failed."""
    _login(client, "csvuser4")
    response = client.post(
        "/api/quiz/uploadCsv",
        data={},
        content_type="multipart/form-data",
    )
    result = response.get_json()
    assert result["status"] == "failed"


def test_upload_wrong_extension(client):
    """Upload with a .txt file should return failed."""
    _login(client, "csvuser5")
    data = {
        "csv": (io.BytesIO(b"some content"), "notes.txt"),
    }
    response = client.post(
        "/api/quiz/uploadCsv",
        data=data,
        content_type="multipart/form-data",
    )
    result = response.get_json()
    assert result["status"] == "failed"


def test_upload_json_valid_file(client):
    """Valid JSON upload should return success with a quiz code."""
    _login(client, "jsonuser1")
    data = {
        "csv": (io.BytesIO(JSON_VALID.encode("utf-8")), "quiz.json"),
        "quiz_title": "JSON Quiz",
    }
    response = client.post(
        "/api/quiz/uploadCsv",
        data=data,
        content_type="multipart/form-data",
    )
    result = response.get_json()
    assert result["status"] == "success"
    assert "code" in result


def test_upload_json_missing_fields(client):
    """JSON upload with missing required fields should return failed."""
    _login(client, "jsonuser2")
    data = {
        "csv": (io.BytesIO(JSON_MISSING_FIELDS.encode("utf-8")), "bad.json"),
    }
    response = client.post(
        "/api/quiz/uploadCsv",
        data=data,
        content_type="multipart/form-data",
    )
    result = response.get_json()
    assert result["status"] == "failed"


def test_upload_json_invalid_content(client):
    """JSON upload with invalid JSON content should return failed."""
    _login(client, "jsonuser3")
    data = {
        "csv": (io.BytesIO(JSON_INVALID_TEXT.encode("utf-8")), "invalid.json"),
    }
    response = client.post(
        "/api/quiz/uploadCsv",
        data=data,
        content_type="multipart/form-data",
    )
    result = response.get_json()
    assert result["status"] == "failed"
