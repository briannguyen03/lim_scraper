'''
match-client.py

Brian Nguyen 
9-07-2025

Calls the resume-match api with resume/BrianNguyen.pdf and job_desc/...
Saves matches to job_matches.txt
'''
import os, requests, json

RESUME_PATH = "resume/BrianNguyen.pdf"
JOB_DESC_DIR = "job_desc/"
MATCHER_API_URL = "http://localhost:3000/api/upload"

def post_req(files):
    response = requests.post(MATCHER_API_URL, files=files)
    print("✅ Response status:", response.status_code)
    print("📄 Response body:", response.json())
    with open("job_matches.txt", "w", encoding="utf-8") as f:
            json.dump(response.json(), f, indent=2)
    return response

if __name__ == "__main__":
    job_desc_paths = [
        os.path.join(JOB_DESC_DIR, filename)
        for filename in os.listdir(JOB_DESC_DIR)
        if filename.endswith(".txt")
    ]

    with open(RESUME_PATH, "rb") as resume_file:
        job_files = [(f"job", (os.path.basename(path), open(path, "rb"))) for path in job_desc_paths]

        try:
            files = [("resume", ("BrianNguyen.pdf", resume_file, "application/pdf"))]
            files += [(name, (filename, f, "text/plain")) for name, (filename, f) in job_files]
            post_req(files)
        finally:
            for _, (_, f) in job_files:
                f.close()
