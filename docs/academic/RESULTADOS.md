# Resultados da avaliação

A avaliação de referência contém quatro documentos autorais, 14 trechos e 12 perguntas. Oito perguntas têm resposta documentada, duas são próximas do tema e omitem um dado específico, e duas tratam de assuntos fora do acervo. O experimento final usa o Qwen2.5 3B quantizado em CPU, com RAG few-shot e com geração sem acervo. Consulte os [dados da execução](evidencias/avaliacao.json), o [gabarito](../../evaluation/cases.json) e o [protocolo detalhado](../../evaluation/README.md).

## Recuperação

| k | Precision@k de trechos | Recall@k de evidências | Hit Rate@k de documentos | Recall@k de arquivo e página |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 62,50% | 62,50% | 100% | 87,50% |
| 2 | 50% | 87,50% | 100% | 100% |
| 4 | 31,25% | 100% | 100% | 100% |

As médias usam as 8 perguntas respondíveis e o ranqueamento anterior ao limiar. Cada pergunta tem poucas janelas anotadas. Com dez combinações relevantes de pergunta e trecho, o teto de Precision@4 deste conjunto é 10 ÷ (8 × 4), ou 31,25%. Quatro candidatos permitem cobrir as âncoras, com passagem de material adicional ao LLM. A busca teve mediana de 29,13 ms e média de 29,71 ms na máquina avaliada.

## Respostas e tempos

| Medida | Com RAG | Sem RAG |
| --- | ---: | ---: |
| Chamadas concluídas | 12/12 | 12/12 |
| Todos os conceitos exigidos pela rubrica lexical | 5/8 | 3/8 |
| Documento e página esperados citados | 7/8 | Sem citações nesta condição |
| Todos os conceitos e fonte esperada na mesma resposta | 5/8 | Sem citações nesta condição |
| Recusas nos casos sem evidência | 4/4 | Fora do contrato da condição |
| Mediana ponta a ponta | 8,78 s | 5,15 s |
| Média ponta a ponta | 8,20 s | 5,55 s |

Entre as perguntas sem resposta, a aplicação recusou 2/2 próximas do domínio e 2/2 de outros assuntos. O tempo de RAG inclui busca, geração e validação. O modelo já havia sido usado pelos testes automatizados e o índice da avaliação foi construído para essa execução.

## Leitura dos casos

- **Q01, código da entrega.** O RAG encontrou VETOR-17 e vinculou a resposta ao guia do laboratório em TXT. O modelo sem documentos informou que desconhecia o código específico.
- **Q02, sobreposição.** O RAG citou a primeira página de `pratica-de-rag.pdf` e explicou a preservação de contexto entre trechos. O modelo sem documentos interpretou o exercício como uma atividade de memória.
- **Q04, recuperação de paráfrase.** A âncora de manutenção de automóveis foi recuperada no top-2. A saída RAG foi “A recuperação oferece candidatos que precisam ser lidos no contexto da pergunta.” e o resultado lexical ficou em falha. Citar a página esperada pode acompanhar uma resposta imprecisa. A estimativa lexical do baseline também pode aceitar a hipótese de mecânica automotiva como acerto por palavras-chave.
- **Q05, similaridade de cosseno.** O RAG selecionou a orientação após repetir a pergunta. A independência do comprimento ficou explícita na citação. O baseline explicou o papel da direção e usou “independentemente de suas magnitudes”. A rubrica deixou de reconhecer a cobertura conceitual dessas formulações.
- **Q08, autorização do material.** A evidência sobre autorização estava no acervo. O estado final foi `insufficient`. A recuperação do texto e o resultado de geração registram limitações diferentes.
- **Q10, dimensões do laboratório.** Na rodada anterior, o modelo afirmou que os vetores tinham duas dimensões e citou um texto que não trazia esse dado. A verificação de números foi acrescentada. O estado final foi `insufficient`. [Rodada anterior](evidencias/avaliacao-antes-validacao-numerica.json)
- **Q11, fora do corpus.** O fluxo RAG recusou a pergunta. Na condição livre, o modelo misturou imperadores romanos com Dom Pedro I. O episódio ilustra a necessidade de conferir afirmações fluentes.

## Iterações e limites

O piloto com o prompt inicial cobriu 4 de 8 casos pela rubrica e recusou indevidamente a pergunta do código. A ordem e o teor dos exemplos few-shot foram ajustados. A rodada com o prompt revisto mostrou o problema de atribuição numérica. A rodada final inclui a checagem de quantidades reconhecidas nas citações. Como as mesmas perguntas orientaram os ajustes, os números medem o conjunto de desenvolvimento. Uma avaliação posterior precisa de perguntas independentes. [Piloto](evidencias/avaliacao-piloto.json)

Uma sondagem com o Qwen2.5 7B levou 44,09 s na consulta Q04 com RAG. A rubrica aprovou a saída, embora o modelo repetisse o tema de consertar um carro e citasse um exemplo sobre vender um automóvel. O caso mostra um falso positivo semântico e é insuficiente para comparar os modelos de forma geral. O projeto mantém o 3B como padrão. [Sondagem de 7B](evidencias/comparacao-exploratoria-7b-q04.json)

A concordância por palavras-chave mede cobertura textual. Ela pode ignorar paráfrases e aceitar termos presentes numa conclusão incorreta. A comparação usa o mesmo modelo e as mesmas perguntas, com instruções e formato diferentes para cada condição. O corpus didático, o hardware único e a execução sem repetições por pergunta limitam a extrapolação. Uma citação e um número podem ser textualmente válidos e ainda expressar uma relação incorreta. [Riscos e melhorias](LIMITACOES-E-ETICA.md)
