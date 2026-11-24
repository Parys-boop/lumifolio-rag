# Roteiro da demonstração ao vivo

A apresentação de 02/12/2026 reserva cinco minutos para o uso do Lumifólio, entre os minutos 5 e 10 da exposição. A demonstração deve mostrar o percurso da pergunta até a evidência e terminar com um caso em que a fonte não sustenta o que foi perguntado.

## Preparo antes da apresentação

- Instale as dependências e baixe os modelos usando as instruções do [README](../../README.md). Faça o primeiro carregamento no computador da apresentação e teste novamente antes da aula.
- Deixe `pratica-de-rag.pdf` e `guia-do-laboratorio.txt` na mesma pasta acessível pelo seletor de arquivos. Depois da importação manual dos dois arquivos, carregue os materiais de exemplo para completar o corpus.
- Deixe aberta a pasta de evidências para acessar as capturas sem depender do navegador da apresentação.
- Ensaie o roteiro partindo de uma base vazia ou de uma sessão dedicada à demonstração. Use apenas arquivos produzidos para este projeto.
- Deixe os termos `VETOR-17` e `pratica-de-rag.pdf, página 1` em uma nota para conferir as saídas ao vivo.

## Percurso de 5 minutos

| Tempo relativo | Ação na tela | O que explicar |
| --- | --- | --- |
| 0:00–0:35 | Execute `.\iniciar.cmd` na pasta do projeto, abra `http://127.0.0.1:8765` e identifique a área de documentos e a conversa. | “O aplicativo e o modelo estão neste computador. Vamos carregar uma pequena base de estudo.” |
| 0:35–1:15 | Envie `pratica-de-rag.pdf` e `guia-do-laboratorio.txt`. Confirme a importação e clique em **Carregar materiais de exemplo**. O acervo exibirá quatro arquivos sem duplicar os dois anteriores. | A extração preserva páginas do PDF. O chunking cria janelas, o modelo E5 gera vetores e o ChromaDB os indexa. |
| 1:15–2:10 | Pergunte “Qual código identifica a entrega do laboratório fictício?”. Mostre a resposta e a fonte TXT. | O código VETOR-17 é um fato do acervo. Na avaliação sem documentos, o mesmo modelo não soube informá-lo. |
| 2:10–3:30 | Pergunte “Por que o exercício mantém palavras em comum entre trechos consecutivos?”. Mostre a página 1 de `pratica-de-rag.pdf` e abra os trechos da busca. | A sobreposição preserva o contexto na fronteira. A busca ordena candidatos por cosseno. A citação localiza o excerto de apoio. |
| 3:30–4:30 | Pergunte “Qual é o prazo de entrega do laboratório fictício?”. | Os materiais mencionam o laboratório e omitem o prazo. O retorno esperado informa a insuficiência de evidência. |
| 4:30–5:00 | Mostre as respostas anteriores no histórico e os controles da biblioteca. | Encaminhe a apresentação para recuperação, respostas e limites. |

Se a geração demorar, explique o ranqueamento enquanto a resposta é processada. Priorize a pergunta com citação de página e a pergunta fora do acervo.

## Plano B

Abra as evidências na ordem do percurso. Mostre o acervo importado, a resposta com a página, os trechos recuperados e a recusa documental. Identifique o que ocorreu na execução ao vivo e diferencie aquele estado da evidência previamente capturada. Deixe disponível no computador da apresentação a [gravação real de 59 segundos](evidencias/demonstracao-real.webm) e as [oito capturas](evidencias/README.md). A gravação é do navegador e está sem locução.

Para produzir uma gravação de contingência adicional, compartilhe apenas a janela do navegador, execute o percurso do quadro em ordem e inicie a gravação quando a página estiver visível. Pause alguns segundos nas fontes e no retorno de insuficiência para que os textos fiquem legíveis em tela cheia. Depois confira início, áudio, legibilidade e ausência de dados pessoais.

## Estrutura da apresentação completa

| Minutos | Conteúdo |
| --- | --- |
| 0–2 | Equipe, público e problema |
| 2–5 | Extração, chunking, vetores, recuperação e prompts |
| 5–10 | Demonstração funcional |
| 10–13 | Resultados e limitações com números do experimento |
| 13–15 | Conclusão e aprendizados |
| 15–20 | Arguição |

Todos os integrantes devem apresentar uma parte. Distribuam as falas e façam um ensaio de até 15 minutos de apresentação, seguido de 5 minutos de arguição. [Guia original](GUIA-DA-ATIVIDADE.html)
