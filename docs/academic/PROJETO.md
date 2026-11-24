# Lumifólio

**Assistente de estudos com recuperação aumentada por geração (RAG)**

| Informação acadêmica | Valor |
| --- | --- |
| Instituição | FATEC Jales |
| Curso | Análise e Desenvolvimento de Sistemas |
| Disciplina | Inteligência Artificial e Aprendizagem de Máquina |
| Atividade | AV_FINAL — Desenvolvimento de Solução com Inteligência Artificial |
| Tema escolhido | Tema 6 — Assistente de Estudos com RAG |
| Entrega e apresentação | 02/12/2026 |

## Problema e público-alvo

Estudantes consultam PDFs, notas e roteiros de aula ao revisar provas ou executar práticas. Quando o material se distribui em vários arquivos, localizar a passagem que responde a uma dúvida pode exigir várias buscas. Uma busca por palavras também pode perder formulações equivalentes. Um modelo generativo sem acesso ao material pode produzir uma explicação plausível que diverge do que a turma recebeu.

O Lumifólio foi concebido para estudantes que querem fazer perguntas sobre um acervo pequeno de uma disciplina e conferir a origem das respostas. O material demonstrativo apresenta conceitos de IA e PLN e inclui um laboratório fictício. As regras desse laboratório servem para testar fatos específicos do acervo, como um código de entrega, sem atribuí-los à instituição.

## Objetivos

- Importar PDFs textuais e arquivos TXT, mantendo o vínculo entre cada trecho e seu documento.
- Localizar passagens pela similaridade semântica entre vetores da pergunta e do acervo.
- Gerar respostas com um modelo de linguagem local condicionado pelas passagens recuperadas.
- Mostrar as fontes citadas, as páginas disponíveis e o texto usado como evidência.
- Informar quando o acervo é insuficiente para responder com fundamento.
- Tornar a recuperação observável para que a demonstração explique o funcionamento do RAG.

## Experiência proposta

O estudante carrega os materiais, usa uma pergunta sugerida ou digita a própria dúvida e lê a resposta no histórico da conversa. Pode conferir o texto citado e abrir a lista de trechos da recuperação para entender por que aparecem passagens diferentes. A gestão do acervo permite remover documentos que não devem participar de perguntas futuras.

A proposta atende ao Tema 6 ao combinar busca semântica, contexto dinâmico, modelo generativo e histórico da sessão. Para a comparação experimental, o mesmo modelo pode receber as mesmas perguntas em uma condição sem os materiais. A interface de estudos apresenta o fluxo com recuperação documental.

Consulte [metodologia](METODOLOGIA.md), [arquitetura](ARQUITETURA.md), [roteiro](DEMONSTRACAO.md) e [guia original](GUIA-DA-ATIVIDADE.html).
