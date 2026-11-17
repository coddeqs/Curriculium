import re
from typing import Dict, Any, List, Tuple, Optional
from core.profile import load_master_profile

TECH_DICTIONARY = {
    "react": ["React", "React 19", "React.js", "SPA", "Hooks"],
    "typescript": ["TypeScript", "Tipagem Estática", "Interfaces"],
    "javascript": ["JavaScript", "ES6+", "JS Moderno"],
    "node": ["Node.js", "Express.js", "Backend JS", "NPM"],
    "express": ["Express.js", "REST APIs", "Middlewares"],
    "flutter": ["Flutter", "Dart", "Mobile UI", "Cross-platform"],
    "dart": ["Dart", "Flutter"],
    "tailwind": ["Tailwind CSS", "Tailwind v4", "Design Responsivo"],
    "css": ["CSS3", "Design Responsivo", "Flexbox/Grid"],
    "html": ["HTML5 Semântico", "Acessibilidade"],
    "api": ["RESTful APIs", "Integração de APIs", "JSON", "HTTP/HTTPS"],
    "rest": ["RESTful APIs", "Endpoints", "Arquitetura REST"],
    "ai": ["Google GenAI SDK", "Gemini API", "Engenharia de Prompt", "LLMs"],
    "ia": ["Inteligência Artificial Generativa", "Google Gemini SDK", "Automação com IA"],
    "gemini": ["Google GenAI SDK", "Gemini 2.5", "LLM Integration"],
    "git": ["Git", "GitHub", "Controle de Versão", "Git Flow"],
    "github": ["GitHub", "Pull Requests", "Code Review"],
    "vite": ["Vite", "Build Tool", "HMR", "Performance"],
    "motion": ["Motion (Framer Motion)", "Microinterações", "Animações Web"],
    "dados": ["Análise e Transposição de Dados", "Integridade de Dados"],
    "moodle": ["Moodle LMS", "Plataformas Educacionais", "Arquitetura EAD"],
    "nfe": ["Integração DANFE NFe", "Fluxos Fiscais"],
    "asaas": ["Integração de Gateway de Pagamento", "Webhooks"]
}

def extract_job_keywords(text: str) -> List[str]:
    text_lower = text.lower()
    found = set()
    for key, synonyms in TECH_DICTIONARY.items():
        pattern = r'\b' + re.escape(key) + r'\b'
        if re.search(pattern, text_lower):
            found.add(key)
    return list(found)

def calculate_match_score(job_text: str, profile: Dict[str, Any]) -> Tuple[int, List[str], List[str]]:
    job_keywords = extract_job_keywords(job_text)
    if not job_keywords:
        return 75, ["Desenvolvimento Web", "Git", "JavaScript", "HTML/CSS"], []

    matched = []
    missing = []
    
    # Flatten profile skills
    profile_skills_lower = " ".join([
        " ".join(profile.get("skills", {}).get(cat, []))
        for cat in profile.get("skills", {})
    ]).lower()

    # Add project tech stacks
    for proj in profile.get("projects", []):
        profile_skills_lower += " " + " ".join(proj.get("stack", [])).lower()
        profile_skills_lower += " " + " ".join(proj.get("highlights", [])).lower()

    for kw in job_keywords:
        synonyms = TECH_DICTIONARY.get(kw, [kw])
        if any(s.lower() in profile_skills_lower for s in synonyms) or kw in profile_skills_lower:
            matched.append(synonyms[0])
        else:
            missing.append(synonyms[0])

    total = len(job_keywords)
    match_count = len(matched)
    score = int((match_count / max(total, 1)) * 100)
    # Give base score for solid foundations (Computer Science Degree + Git + Clean Code)
    adjusted_score = min(max(score, 60), 98)

    return adjusted_score, matched, missing

def rank_projects_for_job(job_text: str, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    job_lower = job_text.lower()
    scored_projects = []

    for proj in projects:
        score = 0
        searchable = (
            proj["name"] + " " +
            proj["role"] + " " +
            proj["category"] + " " +
            " ".join(proj["stack"]) + " " +
            " ".join(proj["highlights"])
        ).lower()

        for key, synonyms in TECH_DICTIONARY.items():
            if key in job_lower:
                for syn in synonyms:
                    if syn.lower() in searchable:
                        score += 3
        
        # Check specific triggers
        if "react" in job_lower and "react" in searchable:
            score += 5
        if "node" in job_lower and "node" in searchable:
            score += 5
        if "flutter" in job_lower and "flutter" in searchable:
            score += 8
        if ("ai" in job_lower or "ia" in job_lower or "inteligência" in job_lower) and "genai" in searchable:
            score += 6
        if ("e-commerce" in job_lower or "gestão" in job_lower or "admin" in job_lower) and "royal" in searchable:
            score += 4

        scored_projects.append((score, proj))

    scored_projects.sort(key=lambda x: x[0], reverse=True)
    return [p[1] for p in scored_projects]

def tailor_resume(
    job_title: str,
    job_company: str,
    job_description: str,
    profile: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    if profile is None:
        profile = load_master_profile()

    job_text = f"{job_title} {job_description}"
    match_score, matched_skills, missing_skills = calculate_match_score(job_text, profile)

    # 1. Headline otimizado para o cargo
    job_lower = job_title.lower()
    if "flutter" in job_lower or "mobile" in job_lower:
        tailored_headline = "Desenvolvedor Mobile (Flutter & Dart) | Ecossistema Reativo & Web"
    elif "front" in job_lower or "react" in job_lower:
        tailored_headline = "Desenvolvedor Front-end (React 19, TypeScript, Tailwind CSS & Vite)"
    elif "back" in job_lower or "node" in job_lower:
        tailored_headline = "Desenvolvedor Back-end (Node.js, Express, REST APIs & Integrações)"
    elif "estágio" in job_lower or "estagio" in job_lower:
        tailored_headline = "Estagiário de Desenvolvimento de Software | Ciência da Computação"
    elif "junior" in job_lower or "júnior" in job_lower:
        tailored_headline = "Desenvolvedor de Software Júnior | Full Stack (React, Node, IA & Flutter)"
    else:
        tailored_headline = f"Desenvolvedor de Software | Foco em {job_title.split('-')[0].strip()}"

    # 2. Resumo profissional sob medida (direto, técnico e natural, sem clichês)
    tech_highlights = ", ".join(matched_skills[:4]) if matched_skills else "React, TypeScript, Node.js e Flutter"
    tailored_summary = (
        f"Graduando em Ciência da Computação (Estácio, previsão 2026) com experiência prática no "
        f"desenvolvimento de aplicações web e mobile utilizando {tech_highlights}. "
        f"Atuo na construção de sistemas completos, incluindo painéis administrativos, e-commerces, "
        f"integrações com APIs REST e fluxos de pagamento. Busco oportunidade como {job_title.strip()} "
        f"na {job_company} para contribuir no desenvolvimento de software com código organizado e foco em entregas."
    )

    # 3. Ordenação de projetos por relevância direta
    ranked_projects = rank_projects_for_job(job_text, profile.get("projects", []))

    # 4. Organização das Hard Skills com destaque para as pedidas
    tailored_skills = {}
    for cat_key, cat_skills in profile.get("skills", {}).items():
        # Move matched to front
        sorted_cat = sorted(cat_skills, key=lambda s: any(m.lower() in s.lower() for m in matched_skills), reverse=True)
        tailored_skills[cat_key] = sorted_cat

    # 5. Pitch de Apresentação / Carta de Apresentação personalizada (natural e direta)
    top_proj = ranked_projects[0]
    cover_letter = (
        f"Olá,\n\n"
        f"Tenho interesse na vaga de {job_title} na {job_company}. "
        f"Curso Ciência da Computação na Estácio e venho desenvolvendo projetos práticos com {tech_highlights}.\n\n"
        f"Um dos meus projetos recentes é o {top_proj['name']}, onde trabalhei com {', '.join(top_proj['stack'][:4])}. "
        f"Meu código e repositórios estão disponíveis no GitHub: {profile['personal']['github']}.\n\n"
        f"Fico à disposição para conversar sobre a vaga.\n\n"
        f"Atenciosamente,\n"
        f"{profile['personal']['name']}\n"
        f"{profile['personal']['phone']} | {profile['personal']['email']}"
    )

    return {
        "job_title": job_title,
        "job_company": job_company,
        "match_score": match_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "tailored_headline": tailored_headline,
        "tailored_summary": tailored_summary,
        "tailored_skills": tailored_skills,
        "ranked_projects": ranked_projects,
        "experience": profile.get("experience", []),
        "certifications": profile.get("certifications", []),
        "education": profile.get("education", []),
        "languages": profile.get("languages", []),
        "personal": profile.get("personal", {}),
        "cover_letter": cover_letter
    }
