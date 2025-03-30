import requests
import json

# Focus on previously challenging keywords
test_jobs = [
    {
        "name": "Language Models Focus",
        "content": "Expert needed in Language Models, LLM systems, and NLP."
    },
    {
        "name": "Blockchain Focus",
        "content": "Seeking Blockchain developer with experience in distributed ledger technologies."
    },
    {
        "name": "MLOps Specialist",
        "content": "MLOps engineer needed for ML Operations and DevOps integration."
    },
    {
        "name": "Prompt Engineering",
        "content": "Looking for skills in Prompt engineering and design for AI systems."
    }
]

for job in test_jobs:
    print(f"\n=== Testing: {job['name']} ===")
    print(f"Content: {job['content']}")
    
    try:
        response = requests.post(
            "http://localhost:8080/extract-keyword",
            json={"jobContent": job['content']}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"Found {len(result['keywords'])} keywords:")
            for kw in result["keywords"]:
                print(f"  • {kw['name']['en']}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Request error: {e}")