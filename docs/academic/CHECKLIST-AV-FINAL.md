# Checklist da AV_FINAL

**Data definida para entrega e apresentação: 02/12/2026.**

A avaliação tem três entregáveis acadêmicos. A documentação deste pacote prepara o código e o material de apoio. A situação de cada teste e experimento está registrada no documento de evidência correspondente.

## Requisitos do guia do professor

| Item do guia | Correspondência no Lumifólio | Conferência |
| --- | --- | --- |
| Equipe formada | Confirmar nomes, formação e comunicação com o professor. | Pendente de confirmação acadêmica |
| Tema escolhido e aprovado | Tema 6 da lista de temas sugeridos. A aprovação antecipada é explicitamente exigida para tema livre. | Tema escolhido. Registro institucional a confirmar |
| Pelo menos uma técnica de PLN | Extração e normalização documental, chunking e embeddings E5 multilíngues. | [Metodologia](METODOLOGIA.md) e [testes](TESTES.md) |
| Integração com LLM | Ollama e Qwen2.5 para inferência generativa local. | [Testes de integração real](TESTES.md) |
| Engenharia de prompts | Persona, system prompt, variantes zero-shot e few-shot, contexto e JSON. | [Engenharia de prompts](ENGENHARIA-DE-PROMPTS.md) |
| Código roda sem erros | Execução local com importação, consulta, histórico, gestão e erros previstos. | [Testes e execução](TESTES.md) |
| Código funcional e documentado | Instruções de instalação, execução e testes, código modular, README e arquitetura. | [README](../../README.md) e [arquitetura](ARQUITETURA.md) |
| Relatório completo de 8 a 12 páginas | Pacote de transferência para o agente que produzirá o relatório. | PDF acadêmico pendente, fora do escopo de autoria deste pacote |
| Relatório em PDF | Formatado em Arial ou Times New Roman 12, espaçamento 1,5. | Pendente da elaboração do relatório |
| Demonstração testada várias vezes | Roteiro com importação, evidências, fontes e recusa. Consultar ensaios técnicos registrados. | [Roteiro](DEMONSTRACAO.md) e [testes](TESTES.md) |
| Plano B | Evidências do navegador e roteiro para contingência. | [Demonstração](DEMONSTRACAO.md) e [handoff](HANDOFF-PERPLEXITY.md) |
| Apresentação ensaiada em até 15 minutos | Cronograma da fala e arguição de 5 minutos. | Pendente de ensaio pela equipe |
| Todos os integrantes dominam suas partes | Distribuir falas e preparar arguição sobre arquitetura, fontes e limites. | Pendente de confirmação pela equipe |
| Credenciais protegidas | Modelo local, configuração de exemplo e exclusões de dados e credenciais do Git. | [Testes e revisão](TESTES.md) |
| Entrega no prazo | PDF e link do código antes do início da aula de apresentações. | Pendente de submissão pela equipe |
| Demonstração ao vivo | Uso do sistema no segmento 5:00–10:00. | Percurso preparado. Apresentação oficial pendente |

O resumo do guia menciona equipes de 2 a 3 alunos. A seção de formação, o FAQ e o checklist descrevem 2 a 4. O guia também apresenta prazos diferentes para formação, com duas semanas no cronograma e uma semana na seção específica. Confirme esses pontos com o professor. Os nomes da equipe e do professor não foram informados.

## Critérios de pontuação e evidências

| Critério | Peso | Evidência prevista |
| --- | --- | --- |
| Correção técnica | 3,0 | Execução, PLN, LLM, organização do código e demonstração. |
| Criatividade e originalidade | 1,5 | Processo de estudo com inspeção do ranqueamento e citações verificáveis. |
| Qualidade da documentação | 2,0 | Relatório acadêmico a finalizar, com material técnico, diagrama e referências deste pacote. |
| Apresentação | 2,0 | Percurso operacional, divisão de falas e arguição. |
| Pensamento crítico | 1,5 | Avaliação comparativa, análise de erros, limites e uso responsável. |

## Diferenciais da missão

A interface web, a avaliação quantitativa e a comparação com e sem RAG são diferenciais previstos na missão. O guia lista interface, avaliação quantitativa, comparação e hospedagem em nuvem como itens opcionais. O escopo técnico usa execução local e publicação do código no GitHub. O estado real da publicação, testes, resultados e evidências está no [handoff](HANDOFF-PERPLEXITY.md).

## Conferência técnica da missão

| Funcionalidades solicitadas | Entrega e conferência |
| --- | --- |
| 1–3. Importação PDF/TXT, extração, tratamento e chunking | PyMuPDF, TXT UTF-8, normalização NFC, janelas com overlap e preservação da página. |
| 4–6. Embeddings, vetor persistente e busca semântica | E5 normalizado, ChromaDB e cosseno, com métricas no conjunto de referência. |
| 7–9. Integração LLM, prompt com contexto e resposta fundamentada | Qwen2.5 3B no Ollama, persona, zero-shot e few-shot, schema JSON e checagem de excertos. |
| 10–12. Fontes, sessão e falta de evidência | Arquivo e página quando disponível, histórico da aba, referências curtas e recusa quando falta suporte. |
| 13–15. Gerenciamento, erros e interface responsiva | Biblioteca persistente, exclusão, mensagens para arquivos e modelo, layout desktop e móvel. |
| Diferenciais | Perguntas sugeridas, inspeção dos trechos, métricas reais, comparação sem RAG e roteiro de contingência. |

[Arquitetura](ARQUITETURA.md) · [Testes](TESTES.md) · [Resultados](RESULTADOS.md) · [Evidências](evidencias/README.md)
