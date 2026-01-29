# leadQualifications

AI-Powered Lead Enrichment &amp; Qualification Pipeline This project automates the process of lead discovery and qualification for ABC Company. It uses a hybrid cloud-local architecture to combine the orchestration power of n8n with a custom FastAPI enrichment service powered by Perplexity and Gemini. 2. Technical Component Breakdown
Trigger & Normalization (n8n)
Trigger: Monitors a Google Sheet for new lead entries.

Normalization: A specialized node cleanses incoming data (names and email formatting) to ensure high-quality inputs for the AI models.

Network Infrastructure & Resilience
Given the distributed nature of the system, a backend microservice in FastAPI was implemented and exposed via a Pinggy reverse SSH tunnel. This allows the cloud-based n8n orchestrator to consume a local Natural Language Processing API. The setup ensures error traceability through a global exception flow, maintaining 100% data integrity even during network fluctuations.

AI Chaining Logic (Python)
The enrichment follows a sequential intelligence chain:

Search (Perplexity): Scours the web for the lead's company activities and official website to provide real-time context.

Scoring (Gemini): Takes the raw context and performs a logical evaluation against ABC Company’s ideal customer profile, returning a standardized JSON object with a lead_score and next_action.

Persistence & Error Handling
Success Path: Once the enrichment is complete, the original row in Google Sheets is updated with the AI's findings and the status is set to Done.

Error Path: In the event of a tunnel timeout or API failure, the Error Trigger captures the exception, logs the technical detail, and marks the lead as Error for manual review.

3. Setup & Installation
   Prerequisites
   Python 3.10+

n8n account (Cloud or Desktop)

API Keys for Google AI Studio (Gemini) and Perplexity.

Local Server Setup
Clone the repository and enter the directory.

Create and activate the virtual environment:

Bash

python -m venv .venv
source .venv/bin/activate # On Windows: .venv\Scripts\activate
Install dependencies:

Bash

pip install -r requirements.txt
Run the FastAPI server:

Bash

python main.py
Tunnel Connection
To expose the local server to n8n, run:

Bash

ssh -p 443 -R0:localhost:8000 a.pinggy.io
Note: Update the n8n HTTP Request node with the temporary URL provided by Pinggy.

4. Future Improvements
   Asynchronous Queuing: Implementing a message broker like Redis to handle high-volume lead bursts.

Advanced Deduplication: Using vector embeddings to identify duplicate companies with slightly different names.
