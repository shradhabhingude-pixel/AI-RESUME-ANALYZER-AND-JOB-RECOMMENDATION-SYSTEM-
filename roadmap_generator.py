"""Rule-based weekly learning roadmap for missing skills."""
LEARNING = {
    "python": "Python fundamentals and small data projects", "sql": "SQL queries, joins, and aggregation",
    "excel": "Excel formulas, pivot tables, and data cleaning", "pandas": "Pandas data cleaning and analysis",
    "power bi": "Power BI dashboards and data modeling", "scikit-learn": "Scikit-learn pipelines and model evaluation",
    "fastapi": "FastAPI endpoints and model serving", "docker": "Docker images, containers, and deployment",
    "mlflow": "MLflow experiment tracking and model registry", "cloud": "Cloud deployment fundamentals",
    "deep learning": "Neural network fundamentals with a small project", "llm": "Large language model concepts and safe prompting",
    "rag": "Retrieval augmented generation with a small document set", "nlp": "NLP preprocessing, embeddings, and evaluation",
    "transformers": "Transformer models and Hugging Face workflows", "opencv": "OpenCV image processing basics",
    "cnn": "Convolutional neural networks for image classification", "yolo": "YOLO object detection and evaluation",
}

def build_roadmap(missing_skills: list[str]) -> list[tuple[str, str]]:
    if not missing_skills:
        return [("Next step", "Choose a project to deepen your skills and keep your resume current.")]
    return [(f"Week {i}", LEARNING.get(skill.casefold(), f"Study {skill} fundamentals and complete a practical project"))
            for i, skill in enumerate(missing_skills[:4], 1)]
