# Roteiro da apresentação e do vídeo executivo

Material de apoio para montar os slides (público não técnico) e gravar o vídeo de até 5 minutos.
Todos os gráficos citados estão em [`reports/figures/`](figures/).

---

## Slides (13 slides)

Regra geral: **um recado por slide**. O título do slide é a conclusão, não o tema.

| # | Título do slide (a mensagem) | Conteúdo | Visual |
|---|---|---|---|
| 1 | **NPS Preditivo: como antecipar a insatisfação do cliente** | Nome do projeto, integrantes, Tech Challenge Fase 1 | Capa |
| 2 | **De cada 100 clientes, 84 são detratores** | E-commerce cresceu; NPS de -80; a nota só chega depois que a jornada acabou, quando já não dá para recuperar o cliente | `01_nps_regua.png` |
| 3 | **A pergunta: o que faz um cliente ficar satisfeito, e como agir antes da pesquisa?** | Pergunta da análise + pergunta do modelo: "qual nota este cliente tende a dar, antes de perguntarmos a ele?" | Texto grande, sem gráfico |
| 4 | **Quatro fatores operacionais explicam a nota; o perfil do cliente, não** | Atraso, reclamações, contatos e tempo de resolução. Região, idade, valor do pedido, desconto e frete não fazem diferença | `03_fatores_correlacao.png` |
| 5 | **Entregar em 14 dias não irrita o cliente; atrasar, sim** | Prazo longo tem o mesmo NPS de prazo curto. O cliente pune a promessa quebrada | `04_prazo_vs_atraso.png` |
| 6 | **No terceiro dia de atraso, o cliente satisfeito desaparece** | No prazo: 18% de promotores. 3 dias de atraso: 97% de detratores. 38,5% dos pedidos já passam desse ponto | `07_ruptura_atraso.png` |
| 7 | **Atraso e atendimento se somam: a nota vai de 8,2 a 1,0** | Quando o atraso obriga o cliente a ligar, o estrago dobra | `06_mapa_atraso_contatos.png` |
| 8 | **Por que isso importa: todo promotor voltou a comprar; nenhum detrator voltou** | 100% x 38% x 0% de recompra em 30 dias | `11_recompra_por_categoria.png` |
| 9 | **Cada dia de atraso custa quase 1 ponto na nota** | Atraso -0,94; reclamação -0,37; contato -0,35; dia de resolução -0,14 | `16_modelo_impacto_fatores.png` |
| 10 | **O modelo funciona como um semáforo de risco antes da pesquisa** | Nota prevista para cada pedido; na faixa Crítico, 100% viraram detratores. Cada pedido sai com o motivo e a área responsável | `15_modelo_faixas_risco.png` + fluxo simples: pedido entregue → nota prevista → faixa de risco → ação da área |
| 11 | **Limitar o atraso a 2 dias vale mais que qualquer melhoria isolada no atendimento** | Simulação: de 4,4 para 5,0 com atraso máximo de 2 dias; 6,5 com atraso zero | `17_simulacao_cenarios.png` |
| 12 | **O que fazer a partir de amanhã** | As recomendações priorizadas (abaixo), cada uma com a área dona | Lista com ícone por área |
| 13 | **O que este estudo não diz** | Limitações e cuidados (abaixo) e próximos passos | Lista curta |

### Slide 12 · Recomendações (texto sugerido)

1. **Logística:** nenhum pedido com mais de 2 dias de atraso. Agir no 1º dia de atraso.
2. **Logística + Produto:** prometer prazos realistas no site.
3. **Atendimento + CRM:** avisar o cliente do atraso antes que ele precise ligar.
4. **Atendimento:** resolver no primeiro contato, em até 3 dias.
5. **Experiência do Cliente:** usar o semáforo do modelo como fila de ação diária.
6. **Comercial:** não usar desconto ou frete para tentar melhorar o NPS; não funciona.
7. **Todos:** medir o efeito de cada ação com teste A/B antes de escalar.

### Slide 13 · Limitações (texto sugerido)

- A base tem sinais de dados simulados: validar com dados reais antes de investir.
- Sem datas: não vemos sazonalidade nem a evolução do cliente.
- O modelo explica metade da variação da nota; a outra metade está fora dos dados.
- Associação não é causa: os ganhos estimados precisam de teste A/B.
- O modelo nunca deve decidir quem recebe a pesquisa de NPS.

**Próximos passos:** validar com dados reais e datados, rodar um piloto do semáforo com grupo de
controle e incluir no modelo dados de produto e de transportadora.

---

## Vídeo executivo (até 5 minutos)

Linguagem de reunião com a liderança: sem termos técnicos, sempre ligando número a decisão. Cerca de
650 palavras (ritmo de fala de ~130 palavras por minuto). Os slides indicados entre colchetes acompanham
a fala.

### 0:00 – 0:30 · Abertura e problema [slides 1 e 2]

> "Boa tarde. Hoje a gente vai falar de um número que preocupa: o NPS da empresa está em **menos
> oitenta**. De cada cem clientes, oitenta e quatro são detratores e só quatro são promotores. E o
> pior: a gente só descobre isso depois que a compra terminou, quando não dá mais para fazer nada por
> aquele cliente."

### 0:30 – 1:00 · A pergunta [slide 3]

> "Por isso, a nossa pergunta foi dupla. Primeiro: o que, na nossa operação, realmente decide se o
> cliente sai satisfeito ou não? E segundo: dá para prever a nota de cada cliente **antes** de mandar
> a pesquisa, para agir enquanto ainda dá tempo?"

### 1:00 – 2:40 · O que os dados mostraram [slides 4 a 8]

> "Analisamos dois mil e quinhentos pedidos. A primeira descoberta: **quatro fatores explicam a nota, e
> todos são da operação**: atraso na entrega, reclamações, contatos com o atendimento e tempo para
> resolver o problema. Região, idade, valor do pedido, desconto, frete: nada disso muda a satisfação.
>
> A segunda descoberta é a mais surpreendente: **o cliente não se importa com a demora, ele se importa
> com o atraso.** Quem recebe em catorze dias está tão satisfeito quanto quem recebe em quatro. O que
> irrita é a promessa quebrada.
>
> E existe um ponto de ruptura claro: **o terceiro dia de atraso.** Quando o pedido chega no prazo,
> dezoito por cento dos clientes viram promotores. A partir do terceiro dia de atraso, praticamente
> todo mundo vira detrator. E hoje, trinta e oito por cento dos nossos pedidos já passam desse ponto.
>
> Os problemas também se somam: pedido no prazo e sem precisar ligar para o atendimento tem nota oito
> vírgula dois. Pedido com quatro dias ou mais de atraso, que obriga o cliente a ligar três vezes, cai
> para um.
>
> E isso vale dinheiro: **todos os promotores voltaram a comprar em trinta dias. Nenhum detrator
> voltou.**"

### 2:40 – 3:40 · A solução: o semáforo de risco [slides 9 e 10]

> "Com esses dados, construímos um modelo que estima a nota de cada pedido assim que ele é entregue,
> antes da pesquisa. Escolhemos o modelo mais simples, porque ele foi o mais preciso e é o mais fácil
> de explicar: ele mostra, por exemplo, que **cada dia de atraso custa quase um ponto na nota**.
>
> Na prática, o modelo vira um semáforo. Cada pedido recebe uma faixa de risco: crítico, alto, atenção
> ou potencial promotor. No teste, **cem por cento dos clientes classificados como críticos realmente
> deram nota de detrator**. E cada pedido já sai com o motivo, atraso ou atendimento, e a área
> responsável. A previsão vira uma fila de trabalho."

### 3:40 – 4:30 · Recomendações [slides 11 e 12]

> "O que propomos: primeiro, **nenhum pedido pode passar de dois dias de atraso**. Pela simulação, só
> isso leva a nota média de quatro vírgula quatro para cinco, mais do que qualquer melhoria isolada no
> atendimento. Segundo, **prometer prazos realistas**, já que prazo longo não incomoda. Terceiro,
> **avisar o cliente do atraso antes que ele precise ligar**. E quarto, usar o semáforo todos os dias:
> pedidos críticos recebem contato e compensação; potenciais promotores, um convite para avaliar e
> indicar a loja."

### 4:30 – 5:00 · Cuidados e fechamento [slide 13]

> "Dois cuidados. Os dados mostram associação, não causa: por isso cada ação deve começar como teste,
> com um grupo de controle, para medir o ganho real. E o modelo nunca deve ser usado para deixar de
> enviar a pesquisa a quem está insatisfeito: isso melhoraria o número e esconderia o problema.
>
> Resumindo: a satisfação do nosso cliente não é sorte nem perfil. Ela é decidida na operação, e agora
> a gente consegue enxergar o problema antes de o cliente responder a pesquisa. Obrigado."
