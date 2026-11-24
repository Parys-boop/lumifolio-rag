# Referências consultadas

Fontes técnicas primárias consultadas na preparação do projeto, em 24 nov. 2026.

| Fonte | Aplicação no projeto |
| --- | --- |
| FATEC Jales. **Guia do Projeto — AV_FINAL — Desenvolvimento de Solução com IA**. Material da disciplina. [Cópia integral fornecida](GUIA-DA-ATIVIDADE.html). | Tema 6, requisitos mínimos, entregáveis, cronograma e critérios. |
| LEWIS, P. et al. **Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks**. 2020. [arXiv 2005.11401](https://arxiv.org/abs/2005.11401). | Referencial de recuperação para geração com acesso a uma fonte de conhecimento externa ao modelo. |
| WANG, L. et al. **Multilingual E5 Text Embeddings: A Technical Report**. 2024. [arXiv 2402.05672](https://arxiv.org/abs/2402.05672). | Base do uso de embeddings multilíngues. |
| INTFLOAT. **Multilingual E5 Small**. [Ficha técnica do modelo](https://huggingface.co/intfloat/multilingual-e5-small) e [revisão fixada](https://huggingface.co/intfloat/multilingual-e5-small/tree/614241f622f53c4eeff9890bdc4f31cfecc418b3). | Dimensão, prefixos de consulta e passagem e interpretação dos escores. |
| SENTENCE TRANSFORMERS. **SentenceTransformer**. [Documentação da classe](https://www.sbert.net/docs/package_reference/sentence_transformer/model.html). | Codificação de textos e normalização dos embeddings. |
| CHROMA. **Configure Collections**. [Documentação](https://docs.trychroma.com/docs/collections/configure). | Configuração da distância de cosseno e parâmetros de coleção. |
| PYMUPDF. **Text**. [Documentação](https://pymupdf.readthedocs.io/en/latest/recipes-text.html). | Extração da camada textual de PDFs. |
| FASTAPI. **Request Files**. [Documentação](https://fastapi.tiangolo.com/tutorial/request-files/). | Recebimento de arquivos enviados pela interface. |
| OLLAMA. **Generate a chat message**. [Documentação da API](https://docs.ollama.com/api/chat). | Chamada local com mensagens de sistema e usuário. |
| OLLAMA. **Structured Outputs**. [Documentação](https://docs.ollama.com/capabilities/structured-outputs). | Resposta em JSON para validação. |
| OLLAMA. **Qwen2.5:3b**. [Variante na biblioteca de modelos](https://ollama.com/library/qwen2.5:3b). | Identificação, quantização, tamanho e licença do modelo usado na geração. |
| OLLAMA. **Qwen2.5:7b**. [Variante na biblioteca de modelos](https://ollama.com/library/qwen2.5:7b). | Modelo alternativo avaliado de forma exploratória em uma consulta. |
| MICROSOFT. **Playwright Python — Videos**. [Documentação](https://playwright.dev/python/docs/videos). | Gravação do fluxo real da aplicação em um navegador com Playwright. |
| PYTORCH. **Installing previous versions of PyTorch**. [Documentação de instalação](https://pytorch.org/get-started/previous-versions/). | Distribuição dos wheels CPU no Windows. |
| GOOGLE. **Prompt design strategies**. [Documentação](https://aistudio.google.com/docs/prompting-strategies). | Referência de instruções claras, exemplos e formato. |
| GOOGLE. **Gemini Developer API Pricing**. [Documentação](https://aistudio.google.com/docs/pricing). | Comparação com opção de nuvem e seus limites de nível gratuito. |
| PYTEST. **How to mark test functions with attributes**. [Documentação](https://docs.pytest.org/en/stable/how-to/mark.html). | Estruturação e seleção de grupos de testes. |

A aplicação usa uma implementação própria de contexto e geração. O artigo de Lewis et al. serve de base conceitual. A integração do Gemini foi considerada na seleção técnica. A documentação do Gemini é referência para estratégias de prompt e comparação com um provedor remoto.
