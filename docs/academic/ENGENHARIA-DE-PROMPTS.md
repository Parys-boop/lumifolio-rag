# Engenharia de prompts

## Design das instruções

| Técnica | Papel no Lumifólio |
| --- | --- |
| System prompt | Define o papel do modelo, as fontes permitidas e a conduta diante de evidência insuficiente |
| Persona | Orienta o modelo a responder como tutor acadêmico e usar linguagem clara em português |
| Zero-shot | Aplica as regras ao contexto e à pergunta sem exemplos no prompt |
| Few-shot | Acrescenta demonstrações da estrutura e do comportamento esperado com exemplos independentes do acervo importado |
| Contexto recuperado | Fornece passagens identificadas para embasar a resposta e localizar as fontes |
| Formatação estruturada | Permite ao programa validar a situação da resposta e as evidências retornadas |

A separação entre instruções e dados é importante porque textos importados podem conter comandos dirigidos ao modelo. A instrução do sistema dá ao conteúdo recuperado a função de evidência documental. O modelo recebe rótulos das passagens e deve apoiar cada referência em uma transcrição delas.

A orientação em caso de insuficiência inclui lacunas em perguntas aparentemente próximas do tema. Por exemplo, uma data de entrega exige uma data presente na evidência. Encontrar um parágrafo sobre a entrega pode ser suficiente para uma resposta sobre o código e insuficiente para uma resposta sobre o prazo.

## Exemplos incluídos no prompt few-shot

O código envia duas interações demonstrativas. A primeira ensina a declarar insuficiência diante de um trecho que menciona o assunto e omite o dado. A segunda mostra que uma passagem pertinente basta para responder e copiar a frase de apoio, mesmo com outra fonte irrelevante.

| Pergunta do exemplo | Trecho F1 | Campos da saída |
| --- | --- | --- |
| Em que ano o cartão foi criado? | O cartão de acesso é azul. | `insufficient`, resposta vazia e lista de citações vazia |
| Qual é a cor do cartão? | O cartão de acesso é azul. O número fica no verso. F2 menciona terminais do laboratório. | `answered`, resposta “O cartão de acesso é azul.” e citação literal dessa frase em F1 |

Os exemplos antecedem a mensagem da pergunta real. No modo zero-shot permanecem a persona, as regras, o esquema e o contexto recuperado.

## Exemplo de comportamento com o acervo

| Entrada | Evidência esperada | Comportamento esperado |
| --- | --- | --- |
| Qual código identifica a entrega do laboratório fictício? | Passagem do `guia-do-laboratorio.txt` contendo `VETOR-17` | Informar o código com o identificador da passagem correspondente |
| Qual é o prazo de entrega do laboratório fictício? | O corpus não especifica um prazo | Declarar ausência de evidência para o prazo |

Estes são exemplos de teste do corpus. A [evidência da avaliação](RESULTADOS.md) registra o comportamento observado. Para citar o conteúdo exato de um prompt no relatório, use a implementação da versão publicada.

## Contrato com o modelo

A aplicação expõe os estados `answered` para resposta sustentada, `insufficient` para evidência insuficiente e `empty` para base vazia. O schema enviado ao Ollama exige `status`, `answer` e `citations`. Cada item de `citations` contém `source` (F1 a F4) e `quote`, uma transcrição de 12 a 500 caracteres. Uma resposta sustentada inclui o texto ao estudante e referências a passagens disponíveis naquele pedido. A aplicação verifica se cada identificador resolve para uma passagem recuperada e se a transcrição está no texto da passagem correspondente. Uma única citação inválida torna a resposta exibida insuficiente. As páginas e os nomes de arquivo são adicionados a partir do índice. Uma segunda checagem exige que números explícitos da resposta também apareçam nos excertos, com equivalências básicas como “duas” e “2”. A validação confirma propriedades do texto e a origem do excerto. A relação semântica entre todos os enunciados da resposta e cada fonte ainda precisa de inspeção.

## Comparação experimental

A condição sem RAG consulta o mesmo modelo para as mesmas perguntas sem anexar trechos. Utiliza uma persona acadêmica, solicita até três frases de conhecimento geral e usa texto livre. O experimento compara fluxos completos com formatos e instruções diferentes. Ela ajuda a observar quando o conhecimento anterior do modelo basta para uma definição geral e quando a pergunta depende de fatos específicos dos materiais. As respostas sem acervo ficam no material de avaliação. Compare também as condições em que ambas produzem uma explicação plausível e só a condição com RAG indica a passagem que pode ser conferida.

O foco é a evidência documental inspecionável. A aplicação pede resposta e trechos de apoio, sem solicitar a exposição de uma cadeia de raciocínio privada. [Ollama — Structured Outputs](https://docs.ollama.com/capabilities/structured-outputs) · [Guia de técnicas de prompting](https://aistudio.google.com/docs/prompting-strategies)
