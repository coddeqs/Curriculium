# 🚀 Curriculium AI — Dev Job Hunter & Resume Tailor

Sistema inteligente de **varredura em tempo real de vagas de desenvolvimento de software** e **adequação estratégica de currículo com IA**, construído sob medida com base no perfil técnico e projetos reais do desenvolvedor **Davi Marçal Silva Araújo** (`@coddeqs`).

---

## 🎯 Por que este sistema foi criado?

O currículo anterior de Davi não refletia a profundidade dos seus projetos práticos em produção. O **Curriculium AI** resolve isso unindo duas frentes:
1. **Radar Ativo nos Maiores Portais (LinkedIn, Gupy, Programathor e GitHub):** Faz a busca automatizada de oportunidades de desenvolvimento (Front-end, Back-end, Full Stack, Mobile Flutter, Estágio e Júnior) nas principais plataformas do mercado:
   - **LinkedIn Jobs:** Busca em tempo real de vagas publicadas no LinkedIn Brasil e em Brasília/DF.
   - **Portal Gupy:** O maior ecossistema de contratação de empresas do Brasil (trilha oficial de inscrição).
   - **Programathor:** Plataforma 100% dedicada a vagas de tecnologia e desenvolvedores.
   - **GitHub Vagas Brasil:** Fóruns abertos da comunidade (`frontendbr`, `backend-br`, `react-brasil`, `flutterbr`).
2. **Resume Tailor com Match ATS:** Analisa a vaga alvo, calcula a compatibilidade técnica (0 a 100%), reorganiza as competências técnicas colocando as exigências da vaga em evidência e seleciona estrategicamente os projetos reais de maior peso do GitHub de Davi para aquela posição específica.
3. **Gerador Oficial de PDF (1 Página ATS-Friendly):** Produz um currículo elegante, moderno, denso e direto, perfeito para triagem automática de plataformas como Gupy, Greenhouse e para recrutadores técnicos.
4. **Pitch de Candidatura Automático:** Redige a carta de apresentação / mensagem para o LinkedIn pronta para envio.

---

## 🛠️ Stack Tecnológica dos Projetos Mapeados no Perfil

- **Royal Tattoo Supply & Studio:** E-commerce e ERP administrativo completo com 11 módulos, DANFE NFe, arquitetura reativa com `Observable Pattern`, Smart Scroll, React 19, Vite, Motion.
- **DA Technologia & DA Gestão:** Plataforma técnica com assistente inteligente integrando a API Gemini (`@google/genai`), prontuário técnico e métricas de desenvolvimento.
- **IV Relojoalheria:** Sistema completo de catálogo de luxo com backend Node.js, Express, REST APIs e IA integrada.
- **GoRunn Ecossistema:** Aplicativo mobile em Flutter/Dart sincronizado com painel web com editor de código CodeMirror.
- **Araujo Perícia:** Aplicação institucional com React 19 e Vite.
- **Moodle COPASA & CCO:** Arquitetura instrucional corporativa e customização de ambientes virtuais de aprendizagem.

---

## 🖥️ Como Executar o Sistema

### Opção 1: Duplo clique no Windows
Basta executar o arquivo:
```cmd
run.bat
```

### Opção 2: Linha de comando
```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```
Acesse no seu navegador: **`http://127.0.0.1:8000`**

---

## 📂 Estrutura de Arquivos

```
Curriculium/
├── app.py                     # API FastAPI e servidor web
├── run.bat                    # Script de execução rápida
├── requirements.txt           # Dependências do projeto
├── core/
│   ├── profile.py             # Leitura e manipulação do perfil mestre
│   ├── scanner.py             # Varredor de vagas (GitHub BR, Remotive, Jobicy)
│   ├── tailor.py              # Motor de inteligência para adequação do currículo e Match Score
│   └── pdf_generator.py       # Gerador de PDF ATS-friendly de 1 página e Markdown
├── data/
│   ├── master_profile.json    # Base de conhecimento de habilidades e projetos de Davi
│   └── saved_resumes/         # Armazenamento dos PDFs customizados gerados
├── templates/
│   └── index.html             # Dashboard interativo com Tailwind CSS e Lucide Icons
└── CURRICULO_ORIGINAL.pdf     # Cópia do currículo original enviado
```

---

## 💡 Recursos da Interface

- **Radar de Oportunidades:** Filtros por React, Node.js, Flutter, Estágio, Júnior e Remoto.
- **Adequação em 1 Clique:** Botão "Adequar Currículo" em qualquer vaga do radar já preenche e analisa os dados instantaneamente.
- **Vaga Externa Customizada:** Cole qualquer descrição do LinkedIn, Gupy ou e-mail de recrutador para gerar um currículo focado.
- **Download Imediato:** Baixe o PDF formatado e pronto para envio.
- **Exportação para Gupy:** Botão para copiar o currículo em texto puro formatado para colar em formulários de candidatura.
