# Lumifólio

**Pacote de contexto para o relatório técnico e a apresentação da AV_FINAL**

| Campo | Informação |
| --- | --- |
| Instituição | FATEC Jales |
| Curso | Análise e Desenvolvimento de Sistemas |
| Disciplina | Inteligência Artificial e Aprendizagem de Máquina |
| Atividade | AV_FINAL — Desenvolvimento de Solução com Inteligência Artificial |
| Tema | 6 — Assistente de Estudos com RAG |
| Entrega e apresentação | 02/12/2026 |
| Código | [Parys-boop/lumifolio-rag](https://github.com/Parys-boop/lumifolio-rag) |
| Versão de referência | [v1.0.0](https://github.com/Parys-boop/lumifolio-rag/tree/v1.0.0) |

O código está em um repositório privado. Este pacote contém o material técnico e as evidências para consulta local. Cite o repositório pela tag. A equipe deve conceder ao avaliador acesso ao repositório antes de entregar o link.

## Problema, solução e fluxo real

Estudantes precisam encontrar respostas em PDFs e textos de uma disciplina, conferir a origem das afirmações e reconhecer quando os materiais deixam uma pergunta em aberto. O Lumifólio permite importar, excluir e consultar documentos PDF com texto selecionável e TXT em UTF-8. O histórico é mantido na aba do navegador e perguntas curtas com referência explícita podem usar a pergunta anterior para orientar a busca.

O backend extrai e normaliza texto, divide as páginas em janelas de 100 palavras com sobreposição de 20 e gera embeddings E5 de 384 dimensões. O ChromaDB persiste os vetores e metadados e recupera até quatro trechos por cosseno. O LLM recebe a pergunta, a memória recente e os trechos acima do limiar de 0,75. O programa valida o JSON, resolve os identificadores para seus documentos e páginas e confere a presença literal das citações e a presença de números explícitos da resposta nesses excertos. Na interface, o estudante pode comparar trechos recuperados, trechos enviados ao modelo e excertos citados.

## Ambiente e modelos

| Componente | Versão usada |
| --- | --- |
| Python | 3.13.12, Windows x64 |
| FastAPI / Uvicorn | 0.135.2 / 0.42.0 |
| Interface | HTML, CSS e JavaScript nativos |
| PyMuPDF | 1.27.2 |
| Sentence Transformers / PyTorch CPU | 5.1.2 / 2.8.0+cpu |
| Transformers / huggingface-hub | 4.57.1 / 0.36.0 |
| Embeddings | intfloat/multilingual-e5-small, revisão 614241f622f53c4eeff9890bdc4f31cfecc418b3 |
| ChromaDB | 1.5.9 |
| Ollama | 0.40.18 |
| LLM principal | qwen2.5:3b, Q4_K_M, digest 357c53fb659c5076de1d65ccb0b397446227b71a42be9d1603d46168015c9e4b |
| HTTPX / Python Multipart | 0.28.1 / 0.0.30 | 9.0.2 / 1.58.0 |
| Microsoft Edge | 155.0.4283.45 |

## Evidências e interpretação

A execução final avaliou 12 perguntas. Nas oito respondíveis, Precision@4 de trechos foi 31,25% e Recall@4 de evidências foi 100%. Pela rubrica lexical, cinco de oito respostas com RAG e três de oito sem RAG cobriram todos os conceitos. Sete respostas com RAG citaram a fonte esperada. As quatro perguntas sem evidência foram recusadas. A mediana foi de 8,78 s com RAG e 5,15 s sem RAG. Passaram 27 testes automatizados, com quatro testes de integração real, e o roteiro de navegador capturou o fluxo de ponta a ponta.

Consulte [RESULTADOS.md](RESULTADOS.md) para os valores finais, tamanhos de amostra, exemplos e limitações. O [JSON de avaliação](evidencias/avaliacao.json) tem as saídas de 12 casos do mesmo LLM com e sem RAG, incluindo ranking e tempos. A [especificação dos casos](../../evaluation/cases.json) fixa respostas, fontes e âncoras. O [protocolo](../../evaluation/README.md) define os denominadores e explica a rubrica lexical.

Use [TESTES.md](TESTES.md) para separar testes com vetores ou respostas simulados, integração real e verificação no navegador. A taxa de recuperação mede a posição das evidências. A qualidade da geração e a precisão das fontes devem ser discutidas separadamente. A checagem literal de citações garante a existência da passagem, enquanto a correspondência semântica de cada afirmação exige revisão.

| Arquivo | Conteúdo |
| --- | --- |
| [01-biblioteca-vazia.png](evidencias/01-biblioteca-vazia.png) | Estado inicial e sugestões |
| [02-arquivo-invalido.png](evidencias/02-arquivo-invalido.png) | Tratamento de PDF inválido |
| [03-biblioteca-indexada.png](evidencias/03-biblioteca-indexada.png) | Quatro documentos e contagem dos trechos |
| [04-resposta-fundamentada.png](evidencias/04-resposta-fundamentada.png) | Resposta do LLM e fonte TXT |
| [05-trechos-e-pagina.png](evidencias/05-trechos-e-pagina.png) | RAG, citação PDF com página e candidatos expandidos |
| [06-pergunta-sem-evidencia.png](evidencias/06-pergunta-sem-evidencia.png) | Recusa diante de dado ausente |
| [07-interface-movel.png](evidencias/07-interface-movel.png) | Layout com largura móvel |
| [08-modelo-indisponivel.png](evidencias/08-modelo-indisponivel.png) | Erro de conexão local e pergunta preservada |
| [demonstracao-real.webm](evidencias/demonstracao-real.webm) | Gravação do navegador em execução real, sem narração |

## Para elaborar o relatório

Observe as nove seções do guia. Produza PDF de 8 a 12 páginas, Arial ou Times New Roman 12 e espaçamento 1,5. A capa deve conter os nomes confirmados dos integrantes e do professor. Redija o resumo em parágrafo único de 5 a 8 linhas. Use o diagrama real da arquitetura, mostre a evidência com página do PDF e compare uma pergunta respondível com outra que exigiu recusa. Trate Gemini como alternativa analisada e identifique quais modelos foram executados. Discuta falsos negativos, suporte semântico, corpus reduzido e privacidade. Cite as referências em ABNT ou formato similar.

- [Guia original do professor](GUIA-DA-ATIVIDADE.html)
- [Problema e objetivos](PROJETO.md)
- [Metodologia, métricas e decisões](METODOLOGIA.md)
- [Arquitetura e diagramas](ARQUITETURA.md)
- [Persona, system prompt, zero-shot, few-shot e JSON](ENGENHARIA-DE-PROMPTS.md)
- [Resultados e comparação](RESULTADOS.md)
- [Testes, ambiente e comandos](TESTES.md)
- [Limitações, ética e trabalhos futuros](LIMITACOES-E-ETICA.md)
- [Referências consultadas](REFERENCIAS.md)

## Para elaborar a apresentação

Reserve 0–2 minutos para equipe e problema, 2–5 para método, 5–10 para demonstração, 10–13 para resultados e limites e 13–15 para conclusão. A arguição ocupa mais cinco minutos. Use o [roteiro ensaiável](DEMONSTRACAO.md) e o [checklist do guia](CHECKLIST-AV-FINAL.md). Inclua o fluxo de recuperação no slide de arquitetura e uma tabela pequena com métricas no slide de resultados. Deixe as capturas e a gravação acessíveis na máquina da apresentação.

## Preenchimento acadêmico

Confirmar nomes dos integrantes, nome do professor, tamanho e registro da equipe, regras de compartilhamento do link, eventual template oficial e horário/canal de entrega. O guia apresenta faixas diferentes para o tamanho da equipe. Consulte a seção correspondente no checklist. A equipe deve elaborar e entregar o PDF final, ensaiar as falas e realizar a apresentação e arguição.
