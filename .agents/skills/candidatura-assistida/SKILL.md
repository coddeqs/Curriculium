---
name: candidatura-assistida
description: Agente de acompanhamento de candidaturas para vagas de desenvolvimento. Prepara o currículo PDF adaptado, gera o pitch de apresentação, auxilia no preenchimento no navegador (pausando em login/CAPTCHA/envio) e registra a candidatura.
---

# Agente de Acompanhamento de Candidaturas (Curriculium AI)

Use este fluxo sempre que o usuário pedir ajuda para se candidatar, enviar solicitação ou acompanhar uma vaga de emprego específica.

## Passo 1: Preparar o Kit da Vaga
1. Carregue o perfil mestre em `data/master_profile.json` via `core/profile.py`.
2. Use `core/tailor.py` (`tailor_resume`) com o título, empresa e descrição da vaga alvo.
3. Gere o currículo PDF de 1 página otimizado via `core/pdf_generator.py` (`generate_resume_pdf`).
4. Extraia também:
   - O **Pitch / Carta de Apresentação** gerado.
   - Os dados rápidos de preenchimento (Nome: Davi Marçal Silva Araújo, E-mail: davimarcal200@gmail.com, Telefone: (61) 99948-7325, Localização: Águas Claras, Brasília/DF, GitHub: https://github.com/coddeqs).

## Passo 2: Acompanhamento no Navegador (Quando houver URL da vaga)
1. Se a vaga tiver um link web (LinkedIn, Gupy, Programathor, etc.), delegue ao subagente `browser` para:
   - Abrir a URL da vaga.
   - Verificar se exige login ou possui CAPTCHA/anti-bot.
   - **Regra obrigatória:** Nunca tentar burlar CAPTCHA ou login. Se exigir autenticação ou verificação humana, pausar imediatamente e avisar o usuário para que ele faça o login/verificação na janela do navegador.
   - Após o login/liberação, auxiliar no preenchimento dos campos básicos (nome, e-mail, telefone, GitHub, resumo/pitch) e fazer upload do PDF gerado (se aplicável, copiando o PDF para `<Artifact Directory Path>/browser_sandbox/uploads/`).
   - **Pausar antes do envio final** para o usuário revisar e confirmar o clique em "Enviar candidatura".

## Passo 3: Vagas por E-mail (ex: GitHub Vagas BR)
1. Se a candidatura for por e-mail, apresente ao usuário:
   - **Para:** e-mail do recrutador
   - **Assunto:** sugestão profissional com o nome da vaga e "Davi Marçal"
   - **Corpo:** o Pitch personalizado gerado pelo `tailor_resume`
   - **Anexo:** caminho clicável do PDF gerado em `data/saved_resumes/`.
