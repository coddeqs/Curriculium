import os
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from core.profile import load_master_profile, save_master_profile
from core.scanner import scan_all_dev_jobs
from core.tailor import tailor_resume
from core.pdf_generator import generate_resume_pdf, generate_resume_markdown

app = FastAPI(title="Curriculium AI - Dev Hunter & Resume Tailor", version="1.0.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
SAVED_DIR = os.path.join(BASE_DIR, "data", "saved_resumes")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(SAVED_DIR, exist_ok=True)

class TailorRequest(BaseModel):
    job_title: str
    job_company: str
    job_description: str

class ProfileUpdateRequest(BaseModel):
    profile: Dict[str, Any]

@app.get("/", response_class=HTMLResponse)
async def read_dashboard():
    index_file = os.path.join(TEMPLATES_DIR, "index.html")
    if not os.path.exists(index_file):
        raise HTTPException(status_code=404, detail="Template not found")
    with open(index_file, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/profile")
async def get_profile():
    return load_master_profile()

@app.post("/api/profile")
async def update_profile(data: ProfileUpdateRequest):
    save_master_profile(data.profile)
    return {"status": "success", "message": "Perfil mestre atualizado com sucesso!"}

@app.get("/api/jobs")
async def get_jobs(
    q: str = Query("", description="Palavra-chave ou tecnologia"),
    level: str = Query("todos", description="Nível: todos, estágio, júnior, pleno"),
    location: str = Query("todos", description="Localização: todos, brasilia, remoto_br"),
    portal: str = Query("todos", description="Portal: todos, linkedin, gupy, programathor, github"),
    no_english: bool = Query(True, description="Sem necessidade de inglês fluente"),
    brazil_only: bool = Query(True, description="Somente vagas brasileiras"),
    exclude_senior: bool = Query(True, description="Anti-filtro: Excluir vagas para Sênior / Lead"),
    exclude_terms: str = Query("", description="Anti-filtro: Termos proibidos separados por vírgula")
):
    jobs = scan_all_dev_jobs(
        search_query=q,
        level_filter=level,
        location_filter=location,
        portal_filter=portal,
        no_fluent_english=no_english,
        brazil_only=brazil_only,
        exclude_senior=exclude_senior,
        exclude_terms=exclude_terms
    )
    return {"total": len(jobs), "jobs": jobs}

@app.post("/api/tailor")
async def process_tailor(req: TailorRequest):
    if not req.job_title.strip():
        raise HTTPException(status_code=400, detail="Título da vaga é obrigatório")
    tailored = tailor_resume(
        job_title=req.job_title,
        job_company=req.job_company or "Empresa Confidencial",
        job_description=req.job_description or ""
    )
    return tailored

@app.post("/api/generate-pdf")
async def create_pdf(req: TailorRequest):
    tailored = tailor_resume(
        job_title=req.job_title,
        job_company=req.job_company or "Empresa",
        job_description=req.job_description or ""
    )
    pdf_path = generate_resume_pdf(tailored)
    filename = os.path.basename(pdf_path)
    return {
        "status": "success",
        "filename": filename,
        "download_url": f"/download/{filename}"
    }

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(SAVED_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Arquivo PDF não encontrado")
    return FileResponse(file_path, media_type="application/pdf", filename=filename)

@app.post("/api/generate-markdown")
async def create_markdown(req: TailorRequest):
    tailored = tailor_resume(
        job_title=req.job_title,
        job_company=req.job_company or "Empresa",
        job_description=req.job_description or ""
    )
    md = generate_resume_markdown(tailored)
    return {"markdown": md}

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
