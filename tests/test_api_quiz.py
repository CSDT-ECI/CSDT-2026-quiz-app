"""Tests for quiz API endpoints in app/api/quiz.py."""
import json


def _login(client, username="quizmaster"):
    """Helper: register and login a user, return the client with session."""
    client.post(
        "/api/add-account",
        data=json.dumps({
            "full_name": "Quiz Master",
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


def test_add_quiz_requires_login(client):
    """Adding a quiz without being logged in should redirect."""
    response = client.post(
        "/api/quiz/add-quiz",
        data=json.dumps({"quiz_title": "Test", "data": []}),
        content_type="application/json",
    )
    assert response.status_code == 302


def test_add_quiz_success(client):
    """Authenticated user should be able to create a quiz."""
    _login(client)
    response = client.post(
        "/api/quiz/add-quiz",
        data=json.dumps({
            "quiz_title": "My Quiz",
            "data": [
                {"question": "What is 1+1?", "a_option": "1", "b_option": "2", "c_option": "3", "answer": "b_option"},
            ],
        }),
        content_type="application/json",
    )
    data = response.get_json()
    assert data["status"] == "success"
    assert "url" in data


def test_get_question_strips_answers(client):
    """Getting quiz questions should not include answers."""
    _login(client)
    # Create a quiz
    create_resp = client.post(
        "/api/quiz/add-quiz",
        data=json.dumps({
            "quiz_title": "Answer Strip Test",
            "data": [
                {"question": "Q1?", "a_option": "A", "b_option": "B", "answer": "a_option"},
            ],
        }),
        content_type="application/json",
    )
    code = create_resp.get_json()["url"].split("/")[-1]

    # Get questions
    response = client.get(f"/api/quiz/getQuestion/{code}")
    questions = response.get_json()
    assert isinstance(questions, list)
    for q in questions:
        assert "answer" not in q


def test_get_question_nonexistent_code(client):
    """Getting questions for a nonexistent quiz should return failed."""
    response = client.get("/api/quiz/getQuestion/nonexistent")
    data = response.get_json()
    assert data["status"] == "failed"


def test_view_quiz_requires_login(client):
    """Viewing quiz details without login should redirect."""
    response = client.get("/api/quiz/view/somecode")
    assert response.status_code == 302


def test_nilai_calculates_score(client):
    """Submitting answers should calculate the score correctly."""
    _login(client, "scorer")
    # Create a quiz with known answers
    create_resp = client.post(
        "/api/quiz/add-quiz",
        data=json.dumps({
            "quiz_title": "Score Test",
            "data": [
                {"question": "Q1?", "a_option": "A", "b_option": "B", "answer": "a_option"},
                {"question": "Q2?", "a_option": "X", "b_option": "Y", "answer": "b_option"},
            ],
        }),
        content_type="application/json",
    )
    code = create_resp.get_json()["url"].split("/")[-1]

    # Submit all correct answers
    response = client.post(
        f"/api/quiz/nilai/{code}",
        data=json.dumps({"quest_0": "a_option", "quest_1": "b_option"}),
        content_type="application/json",
    )
    data = response.get_json()
    assert data["status"] == "success"
    assert data["data"]["score"] == 100


def test_nilai_partial_score(client):
    """Submitting partially correct answers should give partial score."""
    _login(client, "partial")
    create_resp = client.post(
        "/api/quiz/add-quiz",
        data=json.dumps({
            "quiz_title": "Partial Test",
            "data": [
                {"question": "Q1?", "a_option": "A", "b_option": "B", "answer": "a_option"},
                {"question": "Q2?", "a_option": "X", "b_option": "Y", "answer": "b_option"},
            ],
        }),
        content_type="application/json",
    )
    code = create_resp.get_json()["url"].split("/")[-1]

    # Submit 1 correct, 1 wrong
    response = client.post(
        f"/api/quiz/nilai/{code}",
        data=json.dumps({"quest_0": "a_option", "quest_1": "a_option"}),
        content_type="application/json",
    )
    data = response.get_json()
    assert data["status"] == "success"
    assert data["data"]["score"] == 50


def test_my_scores_empty(client):
    """My scores should return empty when user has no scores."""
    _login(client, "noscores")
    response = client.get("/api/quiz/my-scores")
    data = response.get_json()
    assert data["status"] == "success"
    assert data["data"] == []


def test_upload_csv_requires_login(client):
    """Uploading CSV without login should redirect."""
    response = client.post("/api/quiz/uploadCsv")
    assert response.status_code == 302


def test_get_scores_not_logged_in(client):
    """Getting scores without being logged in should fail."""
    response = client.get("/api/quiz/author/someuser/getScores")
    data = response.get_json()
    assert data["status"] == "failed" or data.get("data") == []
