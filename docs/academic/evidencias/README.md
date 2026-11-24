# Evidências do Lumifólio

| Arquivo | Origem |
| --- | --- |
| `avaliacao.json` | Experimento final de 12 perguntas com o Qwen2.5 3B, com e sem RAG. |
| `avaliacao-piloto.json` | Experimento com a primeira redação do prompt de sistema e os primeiros exemplos few-shot. Inclui as falsas recusas que motivaram o ajuste. |
| `avaliacao-antes-validacao-numerica.json` | Rodada com o prompt revisto, antes de exigir suporte textual para números da resposta. | Sondagem de uma pergunta com o Qwen2.5 7B e o prompt revisado. |
| `01` a `08` em PNG | Capturas do Microsoft Edge durante a validação, usando somente o acervo de demonstração. |
| `demonstracao-real.webm` | Gravação da página real durante o teste automatizado no navegador, sem locução. |

Os JSONs mantêm recuperações e saídas efetivamente observadas. Leia [RESULTADOS.md](../RESULTADOS.md) para identificar condições, versões e limitações antes de usar os números no relatório.

O [roteiro da apresentação](../DEMONSTRACAO.md) indica a sequência de contingência. Para reproduzir as capturas, veja o [script de navegador](../../../scripts/browser_e2e.py) e as instruções em [TESTES.md](../TESTES.md).
