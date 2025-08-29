# Resume Screening Application

This repository contains a **Resume Screening Application** built with **Streamlit** and **NLP techniques**. The tool is designed to help recruiters and organizations automatically extract, analyze, and evaluate candidate resumes against job requirements, with a particular focus on **skills matching**.

---

## 🚀 Features
- Upload resumes in PDF format.
- Extract and preprocess resume text.
- Match candidate skills against a predefined **skills lexicon**.
- Calculate a **match score** between the resume and job description.
- Interactive **Streamlit dashboard** for visualization and results.

---

## 📂 Project Structure
```
resume-screening/
│
├── data/                # Contains skills lexicon and related data files
│   └── skills_lexicon.json
│
├── src/                 # Source code for the application
│   ├── nlp_pipeline.py  # NLP pipeline for resume parsing & skill extraction
│   └── streamlit_app.py # Streamlit interface
│
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
└── venv/                # Virtual environment (not included in repo)
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/resume-screening.git
cd resume-screening
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate  # On Mac/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
streamlit run src/streamlit_app.py
```

---

## 🧩 Usage
1. Launch the Streamlit app using the command above.  
2. Upload one or more resumes in **PDF format**.  
3. Provide a job description or required skills.  
4. View the **match score** and extracted insights.  

---

## 📊 Example Workflow
- Upload `resume.pdf`
- Input required job skills: *Python, NLP, Machine Learning*
- Application extracts skills → compares with lexicon → outputs **Match Score: 85%**

---

## 🤝 Contribution Guidelines
Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature-name`)
3. Commit changes (`git commit -m 'Add new feature'`)
4. Push to branch (`git push origin feature-name`)
5. Open a Pull Request

---

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author
Developed by **Elevvo Pathways Team**
