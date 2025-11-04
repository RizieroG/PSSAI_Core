# Overview <!-- omit in toc -->
**PSSAI** è il cuore logico del sistema agentico multi-agente costruito con CrewAI.

Il suo obiettivo è **generare, analizzare e migliorare automaticamente codice PowerShell**, sfruttando una pipeline composta da più agenti LLM (Planner → Coder → Reviewer → Change Planner) e includendo un Human-in-the-Loop per la revisione manuale finale.

Il sistema funziona come un self-evaluation **loop**, in grado di:

- tradurre una richiesta testuale in un piano d’azione;

- generare codice coerente con il piano;

- eseguire analisi statica del codice tramite `PSScriptAnalyzer`;

- correggere automaticamente eventuali errori;

- permettere all’utente di suggerire modifiche e riavviare il ciclo.

## Table of Contents <!-- omit in toc -->

- [Architettura degli Agent](#architettura-degli-agent)
- [Tecniche e Design](#tecniche-e-design)
- [Riferimenti](#riferimenti)


## Architettura degli Agent

Ogni Agent svolge un ruolo specifico nel ciclo di generazione:

| Agent                 | Ruolo                     | Modello                                   | Descrizione                                                                             |
| --------------------- | ------------------------- | ----------------------------------------- | --------------------------------------------------------------------------------------- |
| 🧠 **Planner**        | Pianificazione            | `ollama/dolphin3:8b`                      | Converte la richiesta dell’utente in un piano di 6-9 passi atomici e deterministici.    |
| 💻 **Coder**          | Generazione del codice    | `ollama/gavineke/powershell-codex:latest` | Genera lo script PowerShell eseguibile seguendo il piano e mantenendo le invarianti.    |
| 🔍 **Reviewer**       | Revisione automatica      | `ollama/llama3.1:8b`                      | Analizza il codice e il report JSON di PSScriptAnalyzer, producendo *fix notes* mirate. |
| ✏️ **Change Planner** | Adattamento post-feedback | `ollama/dolphin3:8b`                      | Traduce le richieste di modifica dell’utente in delte concrete del piano iniziale.      |

## Tecniche e Design

- **Multi-Agent Collaboration**: pipeline di agenti specializzati con ruoli indipendenti.

- **Chain-of-Thought reasoning**: usato dal Planner e Coder. 

- **Self-Evaluation**: uso di PSScriptAnalyzer come validatore esterno del codice.

- **Human-in-the-Loop**: integrazione interattiva per suggerire modifiche successive.

- **Iterative Refinement**: ogni iterazione produce un file e un report analitico, tracciabili tramite timestamp.

## Riferimenti

- [CrewAI Documentation](https://docs.crewai.com/)

- [Microsoft PSScriptAnalyzer](https://github.com/PowerShell/PSScriptAnalyzer)

- [Ollama Models](https://ollama.com/library)

- [PowerShell Scripting Docs](https://learn.microsoft.com/en-gb/powershell/)

- [Chain-of-Thought Prompting](https://www.promptingguide.ai/techniques/cot)