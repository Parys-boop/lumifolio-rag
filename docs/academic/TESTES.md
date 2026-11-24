# Testes executados

## Ambiente

Windows x64, AMD Ryzen 7 5700G, 15,3 GiB utilizáveis de RAM, Python 3.13.12, Ollama 0.40.18, PyTorch CPU e Edge 155.0.4283.45. A execução principal usou `qwen2.5:3b` Q4_K_M, com 4.096 tokens de contexto configurados. O Ollama reportou a inferência do modelo em CPU. Consulte o [handoff](HANDOFF-PERPLEXITY.md) para as versões dos componentes.

## Execução automatizada

```powershell
.\preparar.cmd
.\iniciar.cmd
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
$env:HF_HUB_OFFLINE = '1'
$env:LUMIFOLIO_LIVE_TEST = '1'
.venv\Scripts\python.exe -m pytest -q
```

`preparar.cmd` concluiu, `pip check` confirmou que as dependências estavam consistentes e a verificação do encoder produziu um vetor de 384 dimensões. `iniciar.cmd` serviu a interface no endereço local e `/api/status` retornou o modelo baixado.

A suíte final retornou **27 aprovados**. Houve um aviso de depreciação emitido pelo cliente de testes do Starlette sobre HTTPX. O aviso se refere ao cliente de teste e os cenários HTTP foram executados.

| Grupo | Quantidade | Exercício |
| --- | ---: | --- |
| Componentes e API | 23 | UTF-8/BOM, extração por página, dados inválidos, chunking com sobreposição, Chroma persistente com vetores de teste, deduplicação, exclusão, limiar, prompts, conferência de citações, equivalência numérica e origens HTTP. |
| Integração real | 4 | Embedding E5 de 384 dimensões normalizado, Chroma, resposta `VETOR-17` do Ollama e duas recusas com contexto recuperado, sobre prazo e dimensão dos vetores do laboratório. |

Os testes simulam vetores ou respostas somente onde identificados no código. Os testes de conexão usam um endereço local sem serviço e exercitam a falha real de conexão. O grupo `live` usa os pesos locais, o índice Chroma e o serviço Ollama. A aplicação e o roteiro de demonstração executam o LLM efetivamente.

A primeira execução de integração expôs uma falsa recusa para a pergunta sobre o código. O teste manteve a mesma expectativa. O prompt foi revisto e a suíte passou. A revisão independente também encontrou um efeito indevido do histórico em perguntas completas começando com “Por que”. A correção tem regressão automatizada e foi conferida no ranqueamento real, com e sem histórico.

## Navegador, avaliação e revisão

```powershell
.venv\Scripts\python.exe -m playwright install ffmpeg
.venv\Scripts\python.exe -m scripts.browser_e2e --evidence docs\academic\evidencias
.venv\Scripts\python.exe -m evaluation.run --output docs\academic\evidencias\avaliacao.json
```

O teste no Edge passou em desktop de 1.440 × 900 e layout móvel de 390 × 844. Verificou importação de PDF e TXT, arquivo inválido, deduplicação, indicadores, respostas e fontes, página, recusa, histórico após recarga, remoção, ausência de erros de JavaScript e requisições do navegador em loopback. Foram produzidas oito capturas e uma gravação de 59,36 segundos, com abertura conferida no Edge. O script de navegador abre servidores e bases temporárias em loopback. A segunda instância usa uma porta do Ollama sem serviço para verificar o estado de indisponibilidade. A execução de avaliação recria um índice isolado, com o mesmo corpus, sem histórico de conversa. [Resultados e dados](RESULTADOS.md)

O ambiente virtual, a base local, o arquivo `.env`, os pesos e os ZIPs gerados ficam fora da publicação. `.env.example` contém somente parâmetros locais. A revisão confere o conjunto publicado, a integridade do HTML do professor, a ausência de chaves e o escopo das evidências.

Os testes foram executados em uma máquina Windows, com um navegador e uma versão principal do modelo. O corpus é pequeno e a qualidade da resposta em materiais arbitrários continua sujeita a erros de extração, recuperação e geração.
