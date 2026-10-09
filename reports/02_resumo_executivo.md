# Resumo executivo · NPS Preditivo

Base de 2.500 pedidos de um e-commerce nacional (um pedido por cliente), com dados de pedido,
logística, atendimento e a nota de NPS dada depois da compra.

## O cenário

- **NPS da base: -80.** De cada 100 clientes, **84 são detratores**, 11 são neutros e só **4 são
  promotores**. A nota média é 4,4.
- Hoje a empresa só fica sabendo disso **depois** que a jornada termina, quando já não dá para
  recuperar o cliente.

## Perguntas que guiaram o trabalho

- **Análise:** quais fatores operacionais realmente influenciam a satisfação do cliente?
- **Modelo:** assim que o pedido é entregue, e antes da pesquisa, qual nota esse cliente tende a dar?
  Quem precisa de uma ação agora, e por quê?

## Principais insights

1. **Quatro fatores explicam a nota, todos operacionais:** atraso na entrega, reclamações, contatos
   com o atendimento e tempo de resolução. Região, idade, tempo de casa, valor do pedido, desconto,
   frete e parcelamento **não fazem diferença**.
2. **O cliente pune a promessa quebrada, não a espera.** Entregar em 14 dias tem o mesmo NPS de
   entregar em 4 (cerca de -80 nos dois casos). O que derruba a nota é o **atraso** em relação ao
   prazo prometido.
3. **Ponto de ruptura no terceiro dia de atraso.** No prazo, 18% dos clientes são promotores. Com 3
   dias de atraso, 97% são detratores; com 4 ou mais, 100%. **38,5% dos pedidos já passam desse
   ponto.**
4. **Os problemas se somam.** Pedido no prazo e sem contato com o atendimento: nota média 8,2.
   Atraso de 4 dias ou mais com 3 contatos ou mais: nota média 1,0.
5. **O "tipo de cliente" que importa é definido pela experiência, não pelo perfil.** Quem recebeu no
   prazo e não precisou reclamar tem 24% de promotores; quem passou por atraso grande ou muitas
   reclamações tem 0,4%.
6. **Promotor volta a comprar.** 100% dos promotores recompraram em 30 dias; nenhum detrator voltou.

## Quanto cada fator pesa na nota

| A cada... | a nota cai |
|---|---|
| 1 dia de atraso | **0,94 ponto** |
| 1 reclamação a mais | 0,37 ponto |
| 1 contato a mais com o atendimento | 0,35 ponto |
| 1 dia a mais para resolver o problema | 0,14 ponto |

Um pedido sem nenhum desses problemas teria nota prevista de **9,3** (promotor). Só 1 dos 2.500
pedidos chegou a esse cenário.

## O modelo preditivo

- **Estratégia:** regressão linear que prevê a nota de 0 a 10. Foi o modelo de menor erro entre os
  quatro testados (os modelos mais complexos não melhoraram o resultado) e é o mais fácil de explicar.
- **Desempenho no teste:** erra em média **1,4 ponto** na nota, **34% menos** que um chute pela
  média. Separa detratores tão bem quanto um classificador dedicado (ROC-AUC 0,87).
- **Uso:** a nota prevista vira um **semáforo de risco** com ação recomendada:

| Faixa | Nota prevista | Detratores reais no teste | Ação |
|---|---|---|---|
| Crítico | abaixo de 3 | **100%** | Contato proativo, desculpas e compensação; fila prioritária |
| Alto | 3 a 5 | 94% | Avisar sobre o status da entrega antes que o cliente pergunte |
| Atenção | 5 a 7 | 73% | Monitorar e acompanhar após a entrega |
| Potencial promotor | 7 ou mais | 33% (e 31% de promotores) | Pedir avaliação e convidar para indicação |

- Cada pedido sai com o **fator que mais derruba a nota** e a **área responsável** (Logística ou
  Atendimento), o que transforma a previsão em fila de trabalho.

## Quanto vale cada melhoria (simulação com o modelo)

| Cenário | Nota média prevista |
|---|---|
| Hoje | 4,4 |
| 1 contato a menos com o atendimento | 4,7 |
| 1 reclamação a menos por cliente | 4,8 |
| Problemas resolvidos em até 3 dias | 4,8 |
| **Nenhum pedido com mais de 2 dias de atraso** | **5,0** |
| Todo pedido com 1 dia a menos de atraso | 5,3 |
| Atraso zero | 6,5 |

## Recomendações práticas (em ordem de prioridade)

1. **Meta de atraso máximo de 2 dias** (Logística). Acompanhar diariamente os pedidos que entram no
   1º dia de atraso e agir antes do 3º: redespacho, troca de transportadora, cobrança de SLA.
2. **Prometer prazos realistas** (Logística e Produto). Como prazo longo não afeta a nota, exibir um
   prazo com margem de segurança reduz atraso sem precisar entregar mais rápido.
3. **Avisar antes que o cliente precise perguntar** (Atendimento e CRM). Quando o atraso for
   detectado, mandar mensagem proativa com o novo prazo. Isso evita o contato com o atendimento, que
   custa 0,35 ponto cada.
4. **Resolver no primeiro contato** (Atendimento). Meta de resolução em até 3 dias e redução de
   contatos repetidos.
5. **Usar o semáforo do modelo como fila de ação** (Experiência do Cliente). Pedidos Críticos
   recebem contato e compensação; Potenciais promotores recebem convite para avaliar e indicar.
6. **Investigar as reclamações** (Produto e Dados). Entender o que a coluna conta e quais são as
   causas mais frequentes.
7. **Não gastar margem com desconto ou frete para melhorar o NPS** (Comercial). Esses fatores não
   mudam a nota.
8. **Medir o efeito real com teste A/B.** Nos pedidos Críticos, comparar um grupo que recebe a ação
   com um grupo de controle antes de escalar a compensação.

## Limitações e riscos

- **A base tem sinais de dados simulados** (variáveis sem correlação entre si, distribuições
  uniformes). As conclusões devem ser revalidadas com dados reais antes de decisões de investimento.
- **Não há data nem histórico do cliente**: não é possível ver sazonalidade nem validar o modelo ao
  longo do tempo.
- **16% das linhas têm inconsistências** (ex.: atraso maior que o prazo total). Foram mantidas porque
  não mudam as conclusões, mas precisam ser esclarecidas com a área dona do dado, assim como o que a
  coluna de reclamações conta.
- **O modelo explica cerca de metade da variação da nota.** A outra metade depende de fatores que
  não estão na base (produto, expectativa, momento).
- **O modelo identifica mal os promotores**: por isso é usado por faixas de risco.
- **Associação não é causa**: os ganhos da simulação são estimativas para priorizar, a confirmar com
  teste A/B.
- **Risco ético e de métrica:** o modelo **não** deve ser usado para deixar de enviar a pesquisa a
  quem tem risco de ser detrator. O NPS melhoraria no papel e o indicador perderia o valor.
