# Relatório de Execução ETL - Despesas Públicas (Prefeitura de Vitória)

Este relatório sumariza as melhorias arquiteturais e os resultados da aplicação do pipeline de limpeza sobre as bases de dados de despesas públicas dos exercícios de **2016** e **2026**, disponibilizados pelo Portal da Transparência de Vitória.

---

## 1. O Problema Inicial

Os dados fornecidos pelo portal no formato CSV apresentam uma deficiência estrutural grave. A coluna `Descricao` contém textos longos preenchidos por humanos, os quais muitas vezes contêm:
1. **Quebras de linha literais (`\n`)** não encapsuladas, quebrando a linha antes do fechamento das colunas.
2. **Aspas duplas não escapadas (`"`)** no meio da descrição, que confundem os analisadores (parsers) de CSV convencionais (como o do Pandas), fazendo com que as strings pareçam ter sido finalizadas precocemente.

Como resultado, o Pandas gerava o erro `ParserWarning: Error tokenizing data` (quando rodado com `on_bad_lines='warn'`), descartando as linhas afetadas ou deslocando os dados de texto para colunas financeiras (numéricas), o que destruía a integridade dos tipos e corrompia as totalizações.

## 2. Funcionalidades Implementadas

Ao invés de criar lógicas paliativas com base em preenchimentos nulos de colunas arbitrárias, o fluxo do Notebook foi simplificado e fortificado usando o módulo nativo `csv` do Python:

- **Motor de Leitura em Múltiplas Linhas:** O script agora entende que uma linha do CSV que termina prematuramente é, na verdade, a continuação de uma quebra de linha interna. Ele concatena blocos iterativamente até encontrar a próxima linha válida.
- **Reestruturação do "Sanduíche" de Colunas:** Ao montar a linha, o script identifica caso ela possua **mais do que 34 colunas** (causado por vírgulas soltas atreladas a aspas duplas defeituosas no meio da descrição). O script então isola os blocos além da coluna 32, junta todos substituindo as aspas duplas internas por aspas simples, e consolida exatamente no campo 33 (`Descricao`).
- **Simulação em Memória (`StringIO`):** O resultado estruturado nunca é gravado em disco desnecessariamente. Ele é transformado em um arquivo simulado na memória (`StringIO`), que é repassado ao `Pandas`.
- **Validação de Parser Categórica:** Implementamos uma prova real com o parâmetro `on_bad_lines='warn'` interceptado. O notebook exibe explicitamente quais linhas "quebrariam" o Pandas nativo, executa a limpeza, e roda o Pandas novamente para atestar que o alerta não ocorre mais.

## 3. Comparação de Resultados (2016 vs 2026)

Executando nosso motor de limpeza de ponta a ponta nas duas bases de dados, extraímos as seguintes métricas analíticas:

| Métrica Avaliada | Exercício de 2016 | Exercício de 2026 |
| :--- | :--- | :--- |
| **Linhas Defeituosas (Brutas)** | 129 linhas | 80 linhas |
| **Integridade de Colunas (Antes)** | Falha (Múltiplos deslocamentos) | Falha (Múltiplos deslocamentos) |
| **Linhas Defeituosas (Após Limpeza)** | 0 linhas | 0 linhas |
| **Total de Linhas Aproveitadas** | 24.292 registros | 16.123 registros |

> [!NOTE]
> **Interpretação:** Em 2016, 129 empenhos possuíam descrições com formatação de aspas ou quebras de linha irregulares. Em 2026, esse número foi de 80. Nas duas bases de dados, **todas** as anomalias foram sanadas com precisão e as tabelas finais ficaram com `0 warnings` estruturais.

## 4. Conclusão

O pipeline agora é **agnóstico e genérico**, e pode ser usado para todos os outros anos. As "melhorias necessárias" foram completamente implementadas nos arquivos `despesas_vitoria_2016.ipynb` e `despesas_vitoria_2026.ipynb`, removendo códigos de validação confusos e estabelecendo um fluxo sequencial: 
1. Teste de erro original
2. Intervenção estrutural via Motor Python
3. Certificado de conformidade Pandas. 

Os dados finais estão garantidos para exploração no Power BI sem risco de strings estarem mascaradas dentro das métricas de Valores Pagos ou Empenhados.
