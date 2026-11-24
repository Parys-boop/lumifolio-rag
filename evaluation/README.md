# Avaliação reproduzível

Execute na raiz, com o ambiente virtual e o modelo local instalados.

```powershell
.venv\Scripts\python.exe -m evaluation.run --output .runtime\avaliacao.json
```

Para testar apenas o índice, acrescente `--retrieval-only`. Para investigar um caso, acrescente `--case Q02`. A execução gravará a saída integral em JSON e terminará com código 1 se alguma chamada ao modelo falhar. Ela recria o índice em uma base temporária independente dos materiais do usuário.

## Corpus e perguntas

O corpus contém quatro arquivos originais. O arquivo [cases.json](cases.json) contém oito perguntas respondíveis, duas próximas dos temas do corpus para as quais falta informação e duas de outros assuntos. Cada pergunta respondível tem uma resposta de referência, uma ou mais âncoras literais vinculadas a arquivo e página e conceitos usados pela rubrica automática. As âncoras dependem do conteúdo das fontes. As notas dos PDFs são numeradas a partir da primeira página.

## Recuperação

As métricas são calculadas em `k = 1, 2, 4` sobre o ranking gerado antes da decisão de responder. Um trecho é relevante se contém pelo menos uma âncora anotada em arquivo e página correspondentes.

- Precision@k é a quantidade de trechos relevantes nas primeiras k posições dividida por k. Um ranking com menos de k resultados tem as posições vazias contabilizadas no denominador.
- Recall@k de evidências é a fração das âncoras anotadas cobertas pelos trechos recuperados. Âncoras repetidas por sobreposição contam uma vez no numerador do recall.
- Hit Rate@k de documentos é a proporção de consultas com pelo menos um arquivo esperado no top-k.
- Recall@k de fontes é a fração dos pares arquivo/página esperados presentes no top-k. Para TXT, o par inclui uma página nula.

O resumo agrega uma média por consulta respondível. A anotação marca dez combinações de pergunta e trecho relevantes nos oito casos respondíveis. Mesmo um ranking ideal atinge no máximo 31,25% de Precision@4, pois as demais posições são preenchidas por trechos sem âncora anotada. Para os casos sem resposta, o JSON preserva os candidatos e suas similaridades para análise qualitativa.

## Geração e qualidade

As consultas são enviadas ao mesmo modelo local, uma com o fluxo RAG few-shot e outra com instrução zero-shot de resposta geral sem os documentos. A ordem alterna entre casos. Cada pergunta é feita sem histórico. A comparação avalia o efeito da configuração completa, incluindo a mudança de instruções. Uma execução a frio pode levar mais tempo para carregar o modelo. O script registra tempos observados de busca e resposta ponta a ponta por caso, incluindo eventuais recusas antecipadas, sem extrapolar para outros computadores.

As respostas esperadas definem conceitos com alternativas de termos. A rubrica conta os casos em que todos os conceitos foram encontrados após normalização. Ela é uma verificação de cobertura textual. Negação, paráfrases e detalhes adicionais podem exigir leitura humana. As métricas de fonte comparam o par arquivo/página e, como inspeção complementar, relatam quantas citações incluem uma âncora literal. A recusa correta exige o estado `insufficient` e ausência de citações nos quatro casos sem resposta. O baseline pode responder legitimamente às perguntas sobre conhecimento geral, pois recebe uma instrução diferente.

O JSON preserva as perguntas, as respostas entregues pela aplicação, o texto do baseline, as fontes, o ranking com similaridades, os tempos, os modelos usados, o digest do LLM local, as versões das dependências principais e os SHA-256 do corpus e das perguntas. A lista `submitted_ids` mostra se a busca forneceu contexto ao LLM. Quando ela contém trechos e a aplicação retorna uma recusa, o JSON não distingue uma recusa do próprio modelo de uma resposta rejeitada na validação. Os resultados se aplicam ao corpus didático pequeno.
