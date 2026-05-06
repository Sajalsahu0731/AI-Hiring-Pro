from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

job_roles = {
    "Data Analyst": "Analyze data using SQL, Excel, Power BI, Python, and create visualizations to drive business decisions.",
    "Data Scientist": "Develop machine learning models, deep learning architectures, perform statistical analysis using Python.",
    "Web Developer": "Build responsive frontend and scalable backend web applications using HTML, CSS, JavaScript, React, and Node.",
    "Backend Developer": "Design APIs, manage databases, and write server-side logic using Python, Django, Flask, and SQL."
}

def analyze_resume(resume_text):
    roles = list(job_roles.keys())
    descriptions = list(job_roles.values())
    
    job_embeddings = model.encode(descriptions)
    resume_embedding = model.encode(resume_text)
    
    cosine_scores = util.cos_sim(resume_embedding, job_embeddings)[0]
    
    scores = {}
    for i, role in enumerate(roles):
        scores[role] = int(cosine_scores[i].item() * 100)
        
    best_role = max(scores, key=scores.get)
    return scores, best_role