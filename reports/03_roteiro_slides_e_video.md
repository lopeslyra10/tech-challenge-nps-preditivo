# Roteiro da apresentação e do vídeo executivo

Material de apoio para apresentar os slides (público não técnico) e gravar o vídeo de até 5 minutos.
Os gráficos dos notebooks também estão em [`reports/figures/`](figures/), caso precisem das imagens.

---

## Slides (15 slides)

Regra geral: **um recado por slide**. O título do slide é a conclusão, não o tema.

| # | Título do slide (a mensagem) | Conteúdo |
|---|---|---|
| 1 | **NPS Preditivo** | Capa: como antecipar a insatisfação do cliente antes da pesquisa; integrantes |
| 2 | **De cada 100 clientes, 84 são detratores** | NPS de -80 e a divisão entre detratores (84,4%), neutros (11,2%) e promotores (4,4%) |
| 3 | **Hoje a nota chega tarde demais para agir** | Linha da jornada (compra, entrega, atendimento, pesquisa, recompra) com a janela para agir; a pergunta da análise e a do modelo |
| 4 | **Quatro fatores da operação explicam a nota** | Força de cada fator (atraso, reclamações, contatos, tempo de resolução) e o que não muda a nota (perfil do cliente e do pedido) |
| 5 | **A espera não pesa na nota; o atraso pesa** | % de detratores por prazo total (estável, cerca de 85%) e por dias de atraso (de 52% a 99,5%) |
| 6 | **A partir de 3 dias de atraso, quase ninguém fica satisfeito** | Divisão de detratores, neutros e promotores por dia de atraso; 38,5% dos pedidos já estão na zona de ruptura |
| 7 | **Atraso e contatos com o atendimento se somam** | Mapa da nota média: 8,2 no prazo e sem contato; 1,0 com 4 dias ou mais de atraso e 3 contatos ou mais |
| 8 | **Todo promotor voltou a comprar em 30 dias; nenhum detrator voltou** | Recompra de 0% (detratores), 38% (neutros) e 100% (promotores) |
| 9 | **−0,94 ponto na nota a cada dia de atraso** | Slide de destaque: −0,37 por reclamação, −0,35 por contato, −0,14 por dia de resolução; sem nenhum problema, a nota prevista seria 9,3 |
| 10 | **O modelo prevê a nota de cada pedido antes da pesquisa** | Os quatro passos do semáforo e um exemplo real da base (pedido 52035: nota prevista 0,0, risco crítico, Logística age) |
| 11 | **No teste, todos os clientes da faixa Crítico deram nota de detrator** | % de detratores reais por faixa (100%, 94%, 73%, 33%) e a ação de cada faixa |
| 12 | **Limitar o atraso a 2 dias vale mais que qualquer melhoria isolada no atendimento** | Simulação: de 4,4 para 5,0 com atraso máximo de 2 dias; 6,5 com atraso zero |
| 13 | **Seis ações, em ordem de prioridade** | Atraso máximo de 2 dias, prazo realista, aviso proativo, resolução no primeiro contato, semáforo como fila de ação, sem desconto ou frete para subir o NPS |
| 14 | **Limitações e cuidados antes de escalar** | Sobre os dados (simulados, sem datas, inconsistências) e sobre o uso do modelo (metade da variação, associação não é causa, não escolher quem recebe a pesquisa) |
| 15 | **Encerramento** | A satisfação é decidida na operação; próximos passos: dados reais, piloto com grupo de controle, dados de produto e transportadora |

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

### 2:40 – 3:40 · A solução: o semáforo de risco [slides 9 a 11]

> "Com esses dados, construímos um modelo que estima a nota de cada pedido assim que ele é entregue,
> antes da pesquisa. Escolhemos o modelo mais simples, porque ele foi o mais preciso e é o mais fácil
> de explicar: ele mostra, por exemplo, que **cada dia de atraso custa quase um ponto na nota**.
>
> Na prática, o modelo vira um semáforo. Cada pedido recebe uma faixa de risco: crítico, alto, atenção
> ou potencial promotor. No teste, **cem por cento dos clientes classificados como críticos realmente
> deram nota de detrator**. E cada pedido já sai com o motivo, atraso ou atendimento, e a área
> responsável. A previsão vira uma fila de trabalho."

### 3:40 – 4:30 · Recomendações [slides 12 e 13]

> "O que propomos: primeiro, **nenhum pedido pode passar de dois dias de atraso**. Pela simulação, só
> isso leva a nota média de quatro vírgula quatro para cinco, mais do que qualquer melhoria isolada no
> atendimento. Segundo, **prometer prazos realistas**, já que prazo longo não incomoda. Terceiro,
> **avisar o cliente do atraso antes que ele precise ligar**. E quarto, usar o semáforo todos os dias:
> pedidos críticos recebem contato e compensação; potenciais promotores, um convite para avaliar e
> indicar a loja."

### 4:30 – 5:00 · Cuidados e fechamento [slides 14 e 15]

> "Dois cuidados. Os dados mostram associação, não causa: por isso cada ação deve começar como teste,
> com um grupo de controle, para medir o ganho real. E o modelo nunca deve ser usado para deixar de
> enviar a pesquisa a quem está insatisfeito: isso melhoraria o número e esconderia o problema.
>
> Resumindo: a satisfação do nosso cliente não é sorte nem perfil. Ela é decidida na operação, e agora
> a gente consegue enxergar o problema antes de o cliente responder a pesquisa. Obrigado."
