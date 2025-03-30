from fastapi.testclient import TestClient
from src.main import get_app
from src.utils import find_pattern
from httpx import Response
import pandas as pd
import pytest
import os

from ranking_features.utils import SKILLS_DF_FIELDS
from ranking_features.keyword_extraction import ids2text

EXTRACTION_ROUTE = "/extract-keyword"

os.environ['APP_ENV'] = 'test'

app = get_app()
client = TestClient(app)

jobs_df = None
skills_df = None

@pytest.fixture
def skills_df_fixture():
    return pd.read_csv("./data/skills_df.csv", dtype=str)

@pytest.fixture
def pattern_normal():
    return "Ama"

def test_keyword_extraction_with_wrong_format():
    response = client.post(EXTRACTION_ROUTE,
                           json={
                            "jobContet": ""
                            }
                    )

    assert response.status_code == 422

def test_keyword_extraction_with_wrong_format():
    response: Response = client.post("/extract-keyword",
                           json={
                            "jobContet": ""
                            }
                    )

    assert response.status_code == 422

def test_keyword_extraction_with_empty_request():
    with TestClient(app) as client_:
        response:Response = client_.post(EXTRACTION_ROUTE,
                            json={
                                "jobContent": ""
                                }
                        )

        assert response.status_code == 200
        assert response.json()["keywords"] == []

def test_keyword_extraction_with_no_keyword():
    with TestClient(app) as client_:

        response:Response = client_.post(EXTRACTION_ROUTE,
                            json={
                                "jobContent": ""
                                }
                        )
        assert response.status_code == 200
        print(response.text)
        assert response.json()["keywords"] == []

def test_keyword_extraction_with_valid_request():
    with TestClient(app) as client_:

        response:Response = client_.post(EXTRACTION_ROUTE,
                            json={
                                "jobContent": "We are looking for a Quality assurance specialist"
                                }
                        )

        assert response.status_code == 200
        assert len(response.json()["keywords"]) > 0
        assert 'quality assurance specialist' in [keyword['name']['en'].lower() for keyword in response.json()['keywords']]


def test_find_pattern(skills_df_fixture, pattern_normal):
    expected =['Amazon Cloud', 'Amazon EC2', 'Amazon S3', 'Amazon Web Services',
       'Amazon Elastic Cloud Compute', 'Amazon Simple Storage Service',
       'Amazon CloudFront', 'Amazon Simple Email Service']
    matching_skills_ids = find_pattern(pattern_normal, skills_df_fixture, SKILLS_DF_FIELDS)
    actual = ids2text(matching_skills_ids, skills_df_fixture, SKILLS_DF_FIELDS, 'en')
    assert all([_expected in actual for _expected in expected])

def test_suggestion_valid_request():
    with TestClient(app) as client_:
        response:Response = client_.get("search-keywords?pattern=Ama")
        assert response.status_code == 200
        assert response.json()

def test_suggestion_empty_request():
    with TestClient(app) as client_:
        response:Response = client_.get("search-keywords?pattern=!@#!#")
        assert response.status_code == 200
        assert response.json() == []