> [!WARNING]
> **DEPRECATO dal 22 marzo 2026**
> Questo componente non e piu mantenuto.
> Usare solo per storico/riproducibilita. Non usare per nuovi sviluppi.

# Static Analysis • Metriche di Qualità <!-- omit in toc -->

- [Panoramica](#panoramica)
- [Contenuto](#contenuto)
- [Workflow consigliato](#workflow-consigliato)
- [Metriche usate](#metriche-usate)
  - [BLEU (Bilingual Evaluation Understudy)](#bleu-bilingual-evaluation-understudy)
  - [ROUGE-L (Recall-Oriented Understudy for Gisting Evaluation – Longest Common Subsequence)](#rouge-l-recall-oriented-understudy-for-gisting-evaluation--longest-common-subsequence)
  - [METEOR (Metric for Evaluation of Translation with Explicit ORdering)](#meteor-metric-for-evaluation-of-translation-with-explicit-ordering)
  - [Edit Distance (Distanza di Levenshtein)](#edit-distance-distanza-di-levenshtein)
  - [chrF (Character F-score)](#chrf-character-f-score)


## Panoramica

Questo toolkit fornisce una pipeline essenziale per:
1. **tokenizzare** script PowerShell con il parser ufficiale (PSParser);
2. **analizzare** gli script con **PSScriptAnalyzer** (singole coppie o batch);
3. **valutare** la qualità del codice generato tramite metriche standard (BLEU, ROUGE-L, METEOR, Edit Distance, chrF).

È pensato per confrontare uno script **candidato** con uno script di **riferimento**, sia dal punto di vista **statico** (linting/parsing) sia **testuale** (metriche di similarità su token e caratteri).
Le metriche e il flusso CSV sono implementati in `test_evaluation_json_token_complete.py`.

## Contenuto

| File                                     | Ruolo                                                                                                                                               |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tokenization.ps1`                       | Estrae i **token ufficiali** dallo script `.ps1` e salva un **JSON** (compatibile con il valutatore).                                               |
| `pssa_pair_compare.ps1`                  | Confronto **puntuale** tra *uno* script di riferimento e *uno* candidato usando **PSScriptAnalyzer**.                                               |
| `pssa_compare.cmd`                       | Confronto **batch** su più coppie di script con **PSScriptAnalyzer**; utile per report massivi.                                                     |
| `automation_batch.cmd`                   | Esecuzione **batch** del valutatore di metriche su molte coppie; produce/aggiorna un **CSV**.                                                       |
| `test_evaluation_json_token_complete.py` | Calcolo metriche: **BLEU-1/2/4**, **ROUGE-L** (P/R/F), **METEOR**, **EditDistance** (raw/norm), **chrF**; supporta output su **stdout** e **CSV**.  |

**Nota**: `pssa_compare.cmd` è la versione batch di `pssa_pair_compare.ps1`; `automation_batch.cmd` è la versione batch per il calcolo delle metriche.

## Workflow consigliato

1. **Preparazione dati**: metti le coppie `example_X.ps1` (ref) e `example_X_generated.ps1` (cand) nella cartella di lavoro.

2. **Analisi statica**:
    - Con singola coppia: `pssa_pair_compare.ps1` per un report mirato.
    - Con molte coppie: `pssa_compare.cmd` per un report totale.

3. **Tokenizzazione**: esegui `tokenization.ps1` per ciascun file .ps1. Verranno creati i .json con la lista dei token

4. **Valutazione metrica**: usa `automation_batch.cmd`, Il batch scansiona la cartella, invoca ripetutamente il valutatore (`test_evaluation_json_token_complete.py`) e appende i risultati al CSV.

5. **Post-processing (facoltativo)**: puoi generare Excel più complessi utilizzando il CSV generato.

## Metriche usate
Descriviamo brevemente le metriche che sono state utilizzate per confrontare lo script candidato con lo script di riferimento.

### BLEU (Bilingual Evaluation Understudy)

La metrica **BLEU (Bilingual Evaluation Understudy)** valuta quanto il codice generato sia simile a quello di riferimento analizzando la **sovrapposizione delle sequenze di token**, dette *n-gram*. In pratica, misura quante porzioni di codice (costituite da singoli token o da gruppi di token consecutivi) coincidono tra i due script.
Un punteggio BLEU elevato indica che il candidato riutilizza molte sequenze identiche al riferimento, mostrando quindi una forte aderenza strutturale e sintattica al modello originale.

Esistono diverse varianti della metrica, a seconda della lunghezza delle sequenze considerate: BLEU-1 analizza i singoli token e fornisce una stima della copertura lessicale, mentre BLEU-2 e BLEU-4 estendono l’analisi rispettivamente a coppie e quartine di token, permettendo di valutare anche la coerenza e la fluidità delle sequenze nel codice generato.

Nonostante la sua utilità, BLEU presenta un limite importante: non è in grado di cogliere il significato semantico del codice. Due script possono ottenere un punteggio alto pur compiendo operazioni diverse, se la loro struttura sintattica è simile.
I valori di BLEU variano in genere da 0 a 1, dove valori più alti indicano una maggiore somiglianza con il riferimento.

### ROUGE-L (Recall-Oriented Understudy for Gisting Evaluation – Longest Common Subsequence)

La metrica **ROUGE-L (Recall-Oriented Understudy for Gisting Evaluation – Longest Common Subsequence)** valuta la somiglianza tra due testi, o nel nostro caso tra due script, misurando la **lunghezza della sequenza comune più lunga (LCS)** di token condivisa tra il candidato e il riferimento. In altre parole, analizza quanto il codice generato rispetta l’**ordine** dei token presenti nel riferimento, anche se questi non sono necessariamente contigui.

Il punteggio ROUGE-L si basa su tre componenti fondamentali: la **Precisione**, che indica quanto del codice candidato coincide con quello di riferimento; il **Recall**, che misura quanto del riferimento è stato effettivamente riprodotto nel candidato; e infine la **F-measure**, che rappresenta la media armonica tra precisione e richiamo e costituisce il valore principale utilizzato per la valutazione complessiva.

I valori della metrica variano tra **0 e 1**, dove punteggi più elevati indicano una maggiore aderenza strutturale tra i due script. Rispetto a BLEU, ROUGE-L risulta **più tollerante agli scostamenti locali**, poiché riconosce come simili anche porzioni di codice con ordine dei token coerente ma non necessariamente identico o consecutivo.

### METEOR (Metric for Evaluation of Translation with Explicit ORdering)

La metrica **METEOR (Metric for Evaluation of Translation with Explicit ORdering)** valuta il grado di somiglianza tra il codice generato e quello di riferimento, tenendo conto non solo delle corrispondenze esatte tra i token, ma anche di quelle **parziali o semantiche**. A differenza di metriche puramente strutturali come BLEU o ROUGE-L, METEOR è progettata per riconoscere token **con la stessa radice, sinonimi o varianti linguistiche**, offrendo quindi una misura più flessibile e realistica della similarità.

Il suo funzionamento si basa su due principi fondamentali: lo **stemming**, cioè la riduzione dei token alla loro radice comune, e il **matching flessibile**, che consente di associare elementi diversi ma semanticamente vicini. In questo modo, METEOR può attribuire un punteggio parziale anche quando le parole non coincidono perfettamente ma esprimono concetti analoghi.

Il risultato è un indicatore più **semantico** e meno rigido, capace di valutare se il codice generato trasmette lo stesso significato o intento logico del riferimento, anche con formulazioni diverse. I valori di METEOR variano tra **0 e 1**, dove punteggi più alti rappresentano una maggiore affinità concettuale tra i due script.

### Edit Distance (Distanza di Levenshtein)

La **Edit Distance**, o **Distanza di Levenshtein**, misura quanto due testi siano diversi tra loro calcolando il **numero minimo di operazioni necessarie per trasformare uno nell’altro**. Le operazioni considerate sono tre: **inserimento**, **cancellazione** e **sostituzione** di un token (o carattere). In sostanza, questa metrica quantifica il “costo” della trasformazione tra il codice generato e quello di riferimento.

Nel sistema vengono utilizzate due varianti:

* **EditDistance (raw)**, che indica il **numero assoluto di operazioni** richieste per rendere i due script identici;
* **EditNorm**, che rappresenta la **distanza normalizzata** rispetto alla lunghezza maggiore tra i due script, permettendo così di confrontare risultati provenienti da coppie di codice di dimensioni differenti.

L’interpretazione è immediata: **più il valore è basso, maggiore è la somiglianza** tra gli script. In particolare, un’EditNorm pari a **0** indica che i due file sono identici, mentre valori più vicini a **1** segnalano differenze significative nella struttura o nei contenuti. Questa metrica risulta utile per cogliere differenze **micro-strutturali**, come piccoli cambiamenti di token, spostamenti di comandi o variazioni sintattiche minori, che altre metriche più astratte potrebbero non evidenziare.

### chrF (Character F-score)

La metrica **chrF (Character F-score)** valuta la somiglianza tra due testi analizzando la **corrispondenza a livello di caratteri** anziché di token o parole.
Si basa sul calcolo di **Precision** e **Recall** su sequenze di caratteri (*n-gram*), generalmente della lunghezza di 6, combinandole poi in un punteggio F che rappresenta l’equilibrio tra completezza e accuratezza del matching.

Questa metrica è particolarmente utile quando si lavora con **codice sorgente**, poiché è molto sensibile anche a **minime variazioni tipografiche** che possono alterare il comportamento di uno script. Differenze apparentemente insignificanti (come una parentesi mancante, un punto in più o una lettera maiuscola al posto di una minuscola) possono infatti avere effetti funzionali rilevanti.

A differenza di BLEU o ROUGE-L, chrF **non richiede una tokenizzazione complessa**: opera direttamente sulla sequenza di caratteri e riesce quindi a catturare anche refusi o piccoli errori di formattazione che le altre metriche tendono a ignorare.

Il punteggio varia in genere tra **0 e 100**, espresso in forma percentuale: valori più alti indicano una maggiore corrispondenza tra il candidato e il riferimento. In pratica, due script quasi identici ma con piccole discrepanze possono ottenere un punteggio BLEU basso, ma un **chrF elevato**, riflettendo così la loro sostanziale equivalenza strutturale.
