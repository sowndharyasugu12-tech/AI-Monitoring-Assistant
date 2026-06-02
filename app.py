import os
import requests
import google.generativeai as genai
from google.colab import userdata


### setting up API key
genai.configure(
    api_key=userdata.get("GOOGLE_API_KEY")
)

model = genai.GenerativeModel("gemini-2.5-flash")

PROMETHEUS_URL = "http://136.115.103.194/"

### user request

user_question = input("Ask some monitoring question")

### generate promql

promql_prompt = f"""
Convert the following monitoring request into a promql query.

Request: {user_question}

Only return the PromQL query, nothing else.
"""

promql_response = model.generate_content(promql_prompt)

query = promql_response.text.strip()
# Remove markdown formatting from the PromQL query
if query.startswith('```promql') and query.endswith('```'):
    query = query[len('```promql\n'):-len('\n```')].strip()

print(f"PromQL query: \n{query}")

### fetch metrics from prometheus endpoint

response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})

metrics = response.json()

### AI analysis

analysis_prompt = f"""
You are an expert in Kubernetes & Observability

Analyze these prometheus metrics.

User Question:
{user_question}

PromQL Query:
{query}

Metrics:
{metrics}

Provide:
- summary
- root cause analysis
- remediation steps
- resolution summary

Please keep the output concise in 5-6 lines only

"""

analysis_response = model.generate_content(analysis_prompt)

print(f"AI Analysis: \n{analysis_response.text}")
