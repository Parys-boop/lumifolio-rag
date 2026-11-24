# Metodologia

## Construção do acervo e extração

O corpus de demonstração reúne textos didáticos produzidos para o projeto, com conceitos de PLN, embeddings, RAG e interpretação de fontes. Um roteiro de laboratório fictício introduz detalhes específicos que podem ser comparados com as respostas do modelo. Use a lista de casos da avaliação para localizar a fonte esperada de cada pergunta.

O PyMuPDF lê a camada textual de cada página do PDF. Em TXT, a extração decodifica UTF-8 e trata o arquivo como unidade de origem. O texto é normalizado em Unicode NFC, sem hífen condicional e com espaços consecutivos compactados. A aplicação aceita até 50 documentos, com limite de 12 MiB e 500 mil caracteres de texto extraído por arquivo. PDFs têm limite de 300 páginas. A importação também limita a 2.500 trechos por documento. Páginas vazias podem existir em PDFs digitais. Um arquivo sem texto aproveitável requer outra técnica de extração, como OCR.

## Chunking e embeddings

Um fragmento associa uma janela de até 100 palavras ao documento e à página de origem. As janelas avançam 80 palavras, com sobreposição de 20, para conservar parte da vizinhança nos limites. O particionamento por página facilita a rastreabilidade e pode perder relações entre o final de uma página e o início da próxima.

O Sentence Transformers usa o modelo `intfloat/multilingual-e5-small` para projetar perguntas e passagens em vetores de 384 dimensões. O prefixo `passage: ` identifica o texto indexado e `query: ` identifica a consulta. A codificação normaliza cada vetor para norma L2 unitária. Os prefixos seguem o formato descrito na ficha do modelo inclusive para entradas em português. [Ficha do Multilingual E5 Small](https://huggingface.co/intfloat/multilingual-e5-small)

A similaridade entre vetores mede proximidade angular. Para vetores `q` e `d`, o cosseno é `(q · d) / (||q|| ||d||)`. Com vetores unitários, o valor coincide com o produto escalar. O ChromaDB ordena candidatos pela distância de cosseno. A conversão `similaridade = 1 − distância` expressa o ordenamento como escores crescentes de proximidade. A busca considera até quatro trechos. Por padrão, somente candidatos com similaridade de pelo menos 0,75 seguem para a geração. A pontuação depende da distribuição do modelo e do corpus. Um escore de 0,75 não representa 75% de probabilidade de acerto. [Configuração de coleções do ChromaDB](https://docs.trychroma.com/docs/collections/configure)

## Geração e validação

O contexto enviado ao LLM liga cada passagem a uma referência temporária. O prompt define a persona de tutor, orienta o modelo a se restringir às evidências e descreve a forma esperada da resposta. A validação verifica a estrutura, as referências e as citações antes de exibir a resposta. A fonte da citação é resolvida pelo servidor com os metadados do índice. Números explícitos da resposta devem aparecer no conjunto de excertos. A regra reconhece algarismos e numerais curtos de zero e de dois a dez em português.

O Ollama executa `qwen2.5:3b`, uma variante de 3,09 bilhões de parâmetros em quantização Q4_K_M. O peso distribuído pelo Ollama ocupa cerca de 1,9 GB e é baixado separadamente. [Qwen2.5:3b no Ollama](https://ollama.com/library/qwen2.5:3b)

A geração local evita cobrança por chamada e permite que a apresentação continue sem acesso à internet depois do preparo. A documentação de preços do Gemini informa uma modalidade gratuita com acesso e limites dependentes do modelo. A alternativa local evita definir uma credencial do Gemini e transferir trechos para um provedor em nuvem. [Ollama Chat API](https://docs.ollama.com/api/chat) · [Gemini Developer API Pricing](https://aistudio.google.com/docs/pricing)

A API FastAPI disponibiliza as operações para a interface. HTML, CSS e JavaScript viabilizam o controle direto do layout e do fluxo de conversa e fontes com um único servidor Python. Os componentes de recuperação e geração ficam acessíveis a testes por suas interfaces de aplicação. [FastAPI — Request Files](https://fastapi.tiangolo.com/tutorial/request-files/)

## Avaliação reproduzível

O conjunto de referência inclui oito perguntas respondíveis e quatro sem evidência nos documentos. Destas quatro, duas mencionam temas presentes no corpus e duas tratam de outros assuntos. Para cada caso respondível, a avaliação registra o arquivo esperado, a página quando aplicável, âncoras literais e conceitos a procurar na resposta. Perguntas fora do acervo permitem observar recusa indevida ou geração sem suporte.

- **Precision@k** divide o número de trechos com uma âncora do gabarito em arquivo e página correspondentes por k. As posições vazias entram no denominador.
- **Recall@k de evidências** mede a proporção de âncoras esperadas que aparecem entre os k primeiros resultados. **Hit Rate@k de documentos** mede a proporção de perguntas com pelo menos um arquivo esperado no top-k. Os valores de k são 1, 2 e 4.
- **Acerto de fonte e página** distingue a presença no ranqueamento da fonte efetivamente citada na resposta.
- **Latência** mede o tempo observado no ambiente da execução, em que o carregamento inicial pode influenciar o resultado.
- **Comparação com e sem RAG** mantém o modelo e as perguntas. Alterna a ordem das condições e mede a cobertura textual dos conceitos e as citações. A versão com RAG usa few-shot e a geral usa zero-shot. O resultado compara os dois fluxos completos.

O arquivo [RESULTADOS.md](RESULTADOS.md) e os dados estruturados detalham o universo e o denominador de cada medida. Consulte [TESTES.md](TESTES.md) para separar verificações automatizadas, integração real e observações da interface.
