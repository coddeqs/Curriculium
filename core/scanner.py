import json
import os
import re
import time
import urllib.request
import urllib.parse
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CACHE_FILE = os.path.join(DATA_DIR, "cached_jobs.json")

DEV_KEYWORDS = [
    "desenvolvedor", "developer", "engenheiro de software", "software engineer",
    "front-end", "frontend", "back-end", "backend", "full stack", "fullstack",
    "react", "node", "flutter", "dart", "typescript", "javascript", "web",
    "programador", "estágio ti", "estagio ti", "estágio desenvolvimento",
    "junior", "júnior", "estagio", "estágio", "ti", "dev", "tech",
    "python", "api", "software", "ui", "ux", "mobile", "php", "java"
]

FLUENT_ENGLISH_PATTERNS = [
    r'\bingl[êe]s\s+fluente\b',
    r'\bfluent\s+english\b',
    r'\bingl[êe]s\s+avan[çc]ado\b',
    r'\badvanced\s+english\b',
    r'\bconversa[çc][ãa]o\s+em\s+ingl[êe]s\b',
    r'\bconversational\s+english\b',
    r'\benglish\s+(is\s+)?mandatory\b',
    r'\benglish\s+speaking\b',
    r'\benglish\s+proficiency\b',
    r'\bc1\b',
    r'\bc2\b',
    r'\bcommunicating\s+in\s+english\b',
    r'\bdaily\s+in\s+english\b'
]

BRASILIA_PATTERNS = [
    r'\bbras[íi]lia\b',
    r'\bbrasilia\b',
    r'\bdf\b',
    r'\bdistrito\s+federal\b',
    r'\b[áa]guas\s+claras\b',
    r'\btaguatinga\b',
    r'\basa\s+norte\b',
    r'\basa\s+sul\b',
    r'\bplano\s+piloto\b',
    r'\bsudoeste\b',
    r'\bceil[âa]ndia\b',
    r'\bgama\b'
]

SENIOR_EXCLUDE_PATTERN = r'\b(s[êe]nior|sr\.?|lead|tech\s*lead|staff|principal|head|especialista|specialist|expert|coordenador)\b'

def clean_html(text: str) -> str:
    if not text:
        return ""
    clean = re.sub(r'<[^<]+?>', ' ', text)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def is_dev_job(title: str, body: str = "") -> bool:
    text = f"{title} {body}".lower()
    return any(k in text for k in DEV_KEYWORDS)

def requires_fluent_english(text: str) -> bool:
    t = text.lower()
    for pattern in FLUENT_ENGLISH_PATTERNS:
        if re.search(pattern, t):
            return True
    return False

def is_brasilia_location(text: str) -> bool:
    t = text.lower()
    for pattern in BRASILIA_PATTERNS:
        if re.search(pattern, t):
            return True
    return False

def detect_level(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["estágio", "estagio", "intern", "internship", "trainee"]):
        return "Estágio"
    if any(k in t for k in ["júnior", "junior", "jr", "entry", "entry-level", "iniciante"]):
        return "Júnior"
    if any(k in t for k in ["pleno", "mid", "mid-level", "pl"]):
        return "Pleno"
    if any(k in t for k in ["sênior", "senior", "sr", "lead", "staff", "principal"]):
        return "Sênior"
    return "Júnior / Pleno"

def detect_workplace(text: str) -> str:
    t = text.lower()
    if is_brasilia_location(text):
        if any(k in t for k in ["híbrido", "hibrido"]):
            return "Brasília / DF (Híbrido)"
        if any(k in t for k in ["presencial", "alocado"]):
            return "Brasília / DF (Presencial)"
        return "Brasília / DF"
    
    if any(k in t for k in ["100% remoto", "remoto", "remote", "anywhere", "home office", "teletrabalho"]):
        return "100% Remoto (Brasil)"
    if any(k in t for k in ["híbrido", "hibrido", "hybrid"]):
        return "Híbrido"
    return "100% Remoto (Brasil)"

# ==========================================
# 1. GUPY JOBS SCRAPER (PORTAL GUPY.IO)
# ==========================================
def fetch_gupy_jobs(term: str = "desenvolvedor", limit: int = 20) -> List[Dict[str, Any]]:
    jobs = []
    encoded_term = urllib.parse.quote(term or "desenvolvedor")
    url = f"https://portal.gupy.io/job-search/term={encoded_term}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=7) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            script = soup.find('script', id='__NEXT_DATA__')
            if script and script.string:
                data = json.loads(script.string)
                initial = data.get('props', {}).get('pageProps', {}).get('initialJobList', {})
                items = initial.get('data', []) if isinstance(initial, dict) else (initial if isinstance(initial, list) else [])
                
                for item in items[:limit]:
                    title = item.get('name', '').strip()
                    if not title or not is_dev_job(title):
                        continue
                    
                    company = item.get('careerPageName') or "Empresa parceira Gupy"
                    job_url = item.get('jobUrl') or f"https://portal.gupy.io/job-search/term={encoded_term}"
                    
                    workplace_type = item.get('workplaceType', '')
                    city = item.get('city', '') or ''
                    state = item.get('state', '') or ''
                    loc_raw = f"{city} {state} {workplace_type}"
                    
                    is_df = is_brasilia_location(loc_raw) or is_brasilia_location(title)
                    is_remote = workplace_type == 'remote' or 'remot' in loc_raw.lower()
                    
                    if is_df:
                        location_display = "Brasília / DF" if not is_remote else "Brasília / DF (Remoto)"
                    elif is_remote:
                        location_display = "100% Remoto (Brasil)"
                    elif city:
                        location_display = f"{city}/{state}"
                    else:
                        location_display = "100% Remoto (Brasil)"

                    level = detect_level(f"{title} {item.get('type', '')}")
                    fluent_eng = requires_fluent_english(title)

                    jobs.append({
                        "id": f"gupy-{item.get('id', abs(hash(job_url)) % 1000000)}",
                        "title": title,
                        "company": company,
                        "source": "Gupy",
                        "portal": "gupy",
                        "url": job_url,
                        "location": location_display,
                        "is_remote": is_remote,
                        "is_brasilia": is_df,
                        "requires_fluent_english": fluent_eng,
                        "language": "Português",
                        "country": "Brasil",
                        "level": level,
                        "type": "Efetivo / CLT / PJ",
                        "tags": ["Gupy", "Dev", "Brasil"],
                        "published_at": (item.get('publishedDate') or "Recente")[:10],
                        "description": f"Vaga oficial publicada no portal Gupy por {company}. Clique no link para ver a trilha de inscrição completa."
                    })
    except Exception as e:
        print(f"Warning: Gupy fetch error: {e}")
    return jobs

# ==========================================
# 2. LINKEDIN JOBS SCRAPER (LINKEDIN GUEST)
# ==========================================
def fetch_linkedin_jobs(keywords: str = "desenvolvedor", location: str = "Brasil", limit: int = 15) -> List[Dict[str, Any]]:
    jobs = []
    enc_keywords = urllib.parse.quote(keywords or "desenvolvedor")
    enc_location = urllib.parse.quote(location)
    
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={enc_keywords}&location={enc_location}&f_TPR=&position=1&pageNum=0"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=7) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            cards = soup.find_all('div', class_='base-card') or soup.find_all('li')
            
            for card in cards[:limit]:
                title_tag = card.find('h3', class_='base-search-card__title')
                company_tag = card.find('h4', class_='base-search-card__subtitle')
                link_tag = card.find('a', class_='base-card__full-link') or card.find('a')
                loc_tag = card.find('span', class_='job-search-card__location')
                
                title = title_tag.text.strip() if title_tag else ''
                if not title or not is_dev_job(title):
                    continue

                company = company_tag.text.strip() if company_tag else 'Empresa Confidencial'
                job_url = (link_tag.get('href') if link_tag else '#').split('?')[0]
                loc_str = loc_tag.text.strip() if loc_tag else location
                
                is_df = is_brasilia_location(loc_str) or is_brasilia_location(title)
                is_remote = any(k in loc_str.lower() or k in title.lower() for k in ["remoto", "remote", "home office"])
                level = detect_level(title)
                fluent_eng = requires_fluent_english(f"{title} {loc_str}")

                jobs.append({
                    "id": f"linkedin-{abs(hash(job_url)) % 1000000}",
                    "title": title,
                    "company": company,
                    "source": "LinkedIn",
                    "portal": "linkedin",
                    "url": job_url,
                    "location": "Brasília / DF" if is_df else ("100% Remoto (Brasil)" if is_remote else loc_str),
                    "is_remote": is_remote,
                    "is_brasilia": is_df,
                    "requires_fluent_english": fluent_eng,
                    "language": "Português",
                    "country": "Brasil",
                    "level": level,
                    "type": "Tempo Integral / PJ / CLT",
                    "tags": ["LinkedIn", "Dev", "Brasil"],
                    "published_at": "Recente",
                    "description": f"Vaga oficial no LinkedIn anunciada por {company}. Acesse o link para conferir a candidatura simplificada."
                })
    except Exception as e:
        print(f"Warning: LinkedIn fetch error: {e}")
    return jobs

# ==========================================
# 3. PROGRAMATHOR JOBS SCRAPER
# ==========================================
def fetch_programathor_jobs(limit: int = 15) -> List[Dict[str, Any]]:
    jobs = []
    url = "https://programathor.com.br/jobs"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=7) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            cells = soup.find_all('div', class_='cell-list')
            
            for cell in cells[:limit]:
                a = cell.find('a')
                h3 = cell.find('h3')
                title = h3.text.strip() if h3 else (a.text.strip() if a else '')
                if not title or not is_dev_job(title):
                    continue

                href = a.get('href', '') if a else ''
                job_url = ('https://programathor.com.br' + href) if href.startswith('/') else href
                
                # Tags & Company
                info_text = cell.text
                is_df = is_brasilia_location(info_text)
                is_remote = 'remoto' in info_text.lower()
                level = detect_level(title)
                fluent_eng = requires_fluent_english(title)

                jobs.append({
                    "id": f"programathor-{abs(hash(job_url)) % 1000000}",
                    "title": title,
                    "company": "Empresa Tech no Programathor",
                    "source": "Programathor",
                    "portal": "programathor",
                    "url": job_url,
                    "location": "Brasília / DF" if is_df else ("100% Remoto (Brasil)" if is_remote else "Brasil"),
                    "is_remote": is_remote,
                    "is_brasilia": is_df,
                    "requires_fluent_english": fluent_eng,
                    "language": "Português",
                    "country": "Brasil",
                    "level": level,
                    "type": "PJ / CLT",
                    "tags": ["Programathor", "Tech", "Brasil"],
                    "published_at": "Recente",
                    "description": f"Oportunidade especializada para desenvolvedores na plataforma Programathor. Acesse para visualizar a remuneração e se candidatar."
                })
    except Exception as e:
        print(f"Warning: Programathor fetch error: {e}")
    return jobs

# ==========================================
# 4. GITHUB VAGAS BRASIL (COMUNIDADE)
# ==========================================
def scrape_github_repo_issues(repo_name: str) -> List[Dict[str, Any]]:
    jobs = []
    url = f"https://github.com/{repo_name}/issues"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=6) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            
            for a in soup.find_all('a'):
                href = a.get('href', '')
                if f'/{repo_name}/issues/' in href and not any(x in href for x in ['/views', '/templates', '/new', '/comments']):
                    title = a.text.strip()
                    if not title or any(w in title for w in ['ATENÇÃO', 'Regras para', 'Rules for', 'Template']):
                        continue
                    
                    full_url = href if href.startswith('http') else f"https://github.com{href}"
                    workplace = detect_workplace(title)
                    level = detect_level(title)
                    is_df = is_brasilia_location(title)
                    fluent_eng = requires_fluent_english(title)

                    company = "Empresa no Brasil"
                    if " - " in title:
                        parts = title.split(" - ")
                        if len(parts) >= 2:
                            company = parts[0].replace("[", "").replace("]", "").strip()

                    jobs.append({
                        "id": f"gh-{abs(hash(full_url)) % 1000000}",
                        "title": title,
                        "company": company,
                        "source": f"GitHub BR ({repo_name.split('/')[0]})",
                        "portal": "github",
                        "url": full_url,
                        "location": workplace,
                        "is_remote": "remoto" in workplace.lower() or "remote" in workplace.lower(),
                        "is_brasilia": is_df,
                        "requires_fluent_english": fluent_eng,
                        "language": "Português",
                        "country": "Brasil",
                        "level": level,
                        "type": "PJ / CLT / Estágio",
                        "tags": ["GitHub", repo_name.split('/')[0]],
                        "published_at": "Recente",
                        "description": f"Vaga aberta no fórum {repo_name}. Clique no link para conferir a descrição completa e e-mail de contato."
                    })
    except Exception as e:
        pass
    return jobs

def load_cached_jobs_from_disk() -> List[Dict[str, Any]]:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_jobs_to_disk(jobs: List[Dict[str, Any]]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

# ==========================================
# MOTOR PRINCIPAL DE BUSCA AGREGADA
# ==========================================
def scan_all_dev_jobs(
    search_query: str = "",
    level_filter: str = "todos",
    location_filter: str = "todos",      # 'todos', 'brasilia', 'remoto_br'
    portal_filter: str = "todos",        # 'todos', 'linkedin', 'gupy', 'programathor', 'github'
    no_fluent_english: bool = True,      # Não exigir inglês fluente
    brazil_only: bool = True,            # Foco no mercado nacional
    exclude_senior: bool = True,         # Anti-filtro: Excluir vagas para Sênior/Lead
    exclude_terms: str = ""              # Anti-filtro: Palavras proibidas (separadas por vírgula)
) -> List[Dict[str, Any]]:
    all_jobs = []

    # 1. GUPY (Maior portal de RH e TI do Brasil)
    gupy_term = search_query if search_query else ("desenvolvedor brasilia" if location_filter == "brasilia" else "desenvolvedor")
    all_jobs.extend(fetch_gupy_jobs(term=gupy_term, limit=15))

    # 2. LINKEDIN JOBS
    loc_param = "Brasilia, Federal District, Brazil" if location_filter == "brasilia" else "Brasil"
    linkedin_query = search_query if search_query else "desenvolvedor"
    all_jobs.extend(fetch_linkedin_jobs(keywords=linkedin_query, location=loc_param, limit=12))

    # 3. PROGRAMATHOR (Portal especializado em Devs)
    all_jobs.extend(fetch_programathor_jobs(limit=12))

    # 4. GITHUB VAGAS BRASIL (Fóruns abertos da comunidade)
    for repo in ["frontendbr/vagas", "backend-br/vagas", "react-brasil/vagas", "flutterbr/vagas"]:
        all_jobs.extend(scrape_github_repo_issues(repo))

    # Fallback se a internet oscilar
    if not all_jobs:
        all_jobs = load_cached_jobs_from_disk()
    else:
        save_jobs_to_disk(all_jobs)

    filtered = []
    query_terms = [q.lower().strip() for q in search_query.split() if q.strip()]

    # Preparar lista de termos proibidos (Anti-Filtro Customizado)
    banned_terms = [t.lower().strip() for t in exclude_terms.split(",") if t.strip()]

    for job in all_jobs:
        combined = f"{job['title']} {job['company']} {job['location']} {job['description']} {' '.join(job.get('tags', []))}".lower()
        title_lower = job['title'].lower()

        # 1. Filtro: Vaga de TI/Desenvolvimento
        if not is_dev_job(job['title'], job['description']):
            continue

        # 2. ANTI-FILTRO: Excluir vagas para Sênior / Lead / Especialista
        if exclude_senior:
            if re.search(SENIOR_EXCLUDE_PATTERN, title_lower, re.IGNORECASE) or job.get("level") == "Sênior":
                continue

        # 3. ANTI-FILTRO: Termos proibidos customizados pelo usuário
        if banned_terms:
            if any(bt in combined for bt in banned_terms):
                continue

        # 4. Filtro: Portal / Site
        if portal_filter != "todos":
            if job.get("portal", "") != portal_filter:
                continue

        # 5. Filtro: Sem exigência de inglês fluente
        if no_fluent_english and job.get("requires_fluent_english", False):
            continue

        # 6. Filtro: Localização (Brasília / Remoto)
        loc_choice = location_filter.lower().strip()
        if loc_choice == "brasilia":
            if not job.get("is_brasilia", False) and not is_brasilia_location(combined):
                continue
        elif loc_choice == "remoto_br":
            if not job.get("is_remote", False):
                continue

        # 7. Filtro: Nível
        if level_filter.lower() != "todos":
            if level_filter.lower() not in job['level'].lower():
                continue

        # 8. Termos de busca digitados
        if query_terms:
            if not all(term in combined for term in query_terms):
                continue

        filtered.append(job)

    # Remover duplicatas por URL
    seen_urls = set()
    unique_jobs = []
    for j in filtered:
        url_key = j.get("url") or j.get("id")
        if url_key not in seen_urls:
            seen_urls.add(url_key)
            unique_jobs.append(j)

    # Priorizar vagas de Brasília quando o filtro for Brasília
    if location_filter.lower() == "brasilia":
        unique_jobs.sort(key=lambda x: (x.get("is_brasilia", False)), reverse=True)

    return unique_jobs
