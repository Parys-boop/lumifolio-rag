# Limitações, ética e próximos passos

## Cobertura e fundamentação

- A qualidade da resposta depende do acervo importado. Informações desatualizadas, contraditórias ou ausentes aparecem como limitações da evidência disponível.
- O extrator usa a camada textual. PDFs digitalizados como imagem exigem OCR. Tabelas, fórmulas, colunas e infográficos podem perder a ordem de leitura ou relações espaciais.
- As janelas com sobreposição ajudam a conservar a continuidade, mas uma informação dividida entre páginas ou dispersa no acervo pode exigir várias passagens. Um valor pequeno de k acelera as consultas e pode omitir partes importantes.
- A similaridade de cosseno mede proximidade de vetores. Termos próximos do tema podem ter escores altos mesmo quando falta o dado exato solicitado.
- Uma citação literal comprovada pode acompanhar uma interpretação incorreta. O modelo generativo ainda pode misturar fatos, generalizar a evidência ou ignorar ressalvas. A verificação numérica exige que valores reconhecidos apareçam nos excertos. Ela pode recusar grafias numéricas equivalentes fora das regras e aceita valores coincidentes mesmo se a relação estiver errada. A interface permite conferir o trecho e a página no original.
- O corpus de referência é pequeno e produzido para a avaliação. As medidas descrevem esse conjunto e as condições registradas em [resultados](RESULTADOS.md). Acervos diferentes podem alterar cobertura, latência e taxa de recusas.

## Uso responsável dos documentos

Use materiais próprios, públicos ou autorizados. Confirme antes de importar arquivos com dados pessoais, provas fechadas, documentos internos ou conteúdo sigiloso. O uso acadêmico exige distinguir o texto original, a interpretação gerada e a própria conclusão do estudante.

O fluxo local reduz o envio de conteúdo a terceiros, mas o ChromaDB armazena texto e metadados além dos vetores. Proteja a pasta de dados do aplicativo com os controles do sistema operacional. Excluir um documento da interface retira seus trechos das consultas subsequentes. A aba ativa retira da conversa os turnos que recuperaram trechos de documentos excluídos quando atualiza a lista do acervo. Abas abertas separadamente podem manter cópias até nova sincronização. Cópias externas e backups seguem seus próprios controles. Limpe o histórico da sessão antes de usar uma máquina compartilhada.

O servidor foi pensado para execução local e uso individual. Hospedar a instância em rede introduziria necessidades de isolamento, autenticação e gestão de dados. Faça a demonstração com o corpus autoral. Trate a cópia do guia como material fornecido pelo professor e confirme permissão antes de divulgá-la amplamente. Os pesos são baixados à parte. A variante Qwen2.5 de 3 bilhões usa licença de pesquisa da Qwen. [Qwen2.5:3b no Ollama](https://ollama.com/library/qwen2.5:3b)

## Conteúdo que tenta instruir o modelo

Uma passagem pode conter instruções escondidas ou pressionar o modelo a ignorar a pergunta. O system prompt trata os textos como dados e a aplicação valida referências. Essas medidas reduzem algumas classes de falha. A checagem literal identifica uma citação que existe, mas a existência do texto é insuficiente para atestar sua confiabilidade.

## Possíveis melhorias

1. Medir resultados em um conjunto maior de disciplinas, com perguntas rotuladas independentemente por mais de uma pessoa.
2. Ajustar k e o limiar em um conjunto de desenvolvimento separado dos exemplos de teste.
3. Experimentar recuperação híbrida e reordenação para perguntas com identificadores, datas ou termos técnicos raros.
4. Comparar chunking por seção com janelas de tamanho fixo em documentos longos.
5. Avaliar OCR para documentos escaneados e leitura estruturada de tabelas.
6. Medir apoio por afirmação e detectar contradições entre fontes, considerando precisão e impacto no tempo de resposta.
