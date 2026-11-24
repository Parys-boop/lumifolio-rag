# Lumifólio

Assistente de estudos com RAG para consultar materiais acadêmicos em PDF e TXT. Ele recupera trechos por similaridade, envia os candidatos ao modelo local e mostra as fontes citadas com páginas e excertos. Se a informação disponível for insuficiente, o aplicativo registra a ausência de evidência.

Projeto da AV_FINAL de Inteligência Artificial e Aprendizagem de Máquina da FATEC Jales, curso de Análise e Desenvolvimento de Sistemas.

## Instalação no Windows

Instale o Python 3.13 de 64 bits e o [Ollama para Windows](https://ollama.com/download/windows). Abra o Ollama para iniciar o serviço local. A preparação inicial precisa de internet e usa modelos baixados gratuitamente. Reserve espaço para o ambiente virtual e os modelos. O projeto foi validado com 16 GB de RAM.

```powershell
git clone https://github.com/Parys-boop/lumifolio-rag.git
cd lumifolio-rag
.\preparar.cmd
.\iniciar.cmd
```

Abra [Lumifólio em localhost](http://127.0.0.1:8765). O repositório é privado e o clone exige uma conta GitHub com acesso. Se já estiver na pasta do projeto, execute os dois scripts diretamente. A primeira indexação e a primeira resposta podem demorar mais devido ao carregamento dos modelos.

### Comandos equivalentes

```powershell
py -3.13 -m venv .venv
.venv\Scripts\python.exe -m pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cpu
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m lumifolio.embeddings
ollama pull qwen2.5:3b
.\iniciar.cmd
```

Se `ollama` ainda não estiver no PATH, reabra o terminal ou use `preparar.cmd`, que também procura a instalação padrão. A configuração opcional está em `.env.example`. Troque o modelo apenas por um já baixado para execução local. O script de início usa o cache do E5 em modo offline. Para instalar em outra máquina, baixe os pesos antes de desconectar.

## Uso

1. Escolha arquivos ou carregue os quatro materiais didáticos fictícios de exemplo.
2. Escolha uma pergunta sugerida e clique em **Enviar**, ou escreva a sua.
3. Abra **Ver trechos da busca** para conferir a similaridade e os trechos enviados ao LLM.
4. Use **Configurações da resposta** para alternar entre few-shot e zero-shot.
5. Remova materiais pela biblioteca ou inicie uma nova conversa.

A biblioteca persiste localmente em `.runtime/chroma`. Ela armazena trechos normalizados, metadados e embeddings. A conversa fica na sessão da aba. Importe apenas materiais autorizados e mantenha o servidor no endereço de loopback. A aplicação aceita PDF com texto selecionável e TXT em UTF-8. PDFs digitalizados exigem OCR prévio.

## Testes e avaliação

```powershell
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m pytest -q -m 'not live'
$env:LUMIFOLIO_LIVE_TEST = '1'
.venv\Scripts\python.exe -m pytest -q -m live
.venv\Scripts\python.exe -m evaluation.run --output .runtime\avaliacao.json
.venv\Scripts\python.exe -m playwright install ffmpeg
.venv\Scripts\python.exe -m scripts.browser_e2e --evidence .runtime\evidencias
```

O teste de navegador exige Microsoft Edge instalado. Sem a opção `--evidence`, o script roda as verificações sem gravar o fluxo. Consulte o [protocolo da avaliação](evaluation/README.md), os [resultados](docs/academic/RESULTADOS.md) e os [testes executados](docs/academic/TESTES.md).

## Documentação acadêmica

- [Arquitetura e fluxo de dados](docs/academic/ARQUITETURA.md)
- [Engenharia de prompts](docs/academic/ENGENHARIA-DE-PROMPTS.md)
- [Roteiro de demonstração](docs/academic/DEMONSTRACAO.md)
- [Checklist AV_FINAL](docs/academic/CHECKLIST-AV-FINAL.md)
- [Pacote de contexto para o Perplexity](docs/academic/HANDOFF-PERPLEXITY.md)
