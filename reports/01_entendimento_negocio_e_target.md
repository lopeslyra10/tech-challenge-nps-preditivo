# Etapas 1 e 2 · Entendimento do negócio e definição da target

Este documento responde às duas primeiras etapas do desafio, que pedem **pensamento analítico e
entendimento conceitual**, não código. Os números citados vêm da análise exploratória em
[`01_eda_negocio`](../notebooks/01_eda_negocio.ipynb) e da avaliação em
[`03_modelo_preditivo`](../notebooks/03_modelo_preditivo.ipynb).

---

## 1. Entendimento do negócio

### Qual problema de negócio está sendo resolvido?

A empresa cresceu e passou a lidar com muito mais pedidos, entregas e chamados. Ao mesmo tempo, o
NPS varia muito entre clientes que, olhando os indicadores operacionais médios, parecem ter tido a
mesma experiência.

O problema tem duas partes:

1. **Falta de diagnóstico.** A empresa não sabe quais fatores da operação realmente transformam um
   cliente em promotor ou em detrator. Sem isso, investe às cegas: pode gastar com desconto ou
   frete quando o que pesa é outra coisa.
2. **Ação tardia.** O NPS só é coletado quando a jornada já terminou. Quando a nota baixa chega,
   o cliente já teve a experiência ruim e já pode ter decidido não voltar. A empresa reage em vez de
   prevenir.

Em uma frase: **transformar dados operacionais (pedido, logística e atendimento) em um diagnóstico
dos fatores que movem a satisfação e em um alerta antecipado de quem tende a ficar insatisfeito,
para que a empresa aja antes da pesquisa.**

### Por que o NPS é importante para um e-commerce?

- **Trocar de loja custa um clique.** No varejo online o concorrente está na aba ao lado, e a
  lealdade depende quase só da experiência.
- **O crescimento depende de recompra.** Conquistar um cliente novo (mídia paga, marketplace,
  cupom de primeira compra) custa caro. O lucro vem do cliente que volta, e o NPS é um termômetro
  antecipado dessa volta. Na base do desafio, **100% dos promotores recompraram em 30 dias, contra
  nenhum detrator**.
- **A reputação é pública.** Avaliações de produto, notas em marketplace, Reclame Aqui e redes
  sociais influenciam a decisão de compra de quem nunca comprou na loja.
- **É simples e comparável.** Uma pergunta só, entendida por qualquer área, que pode ser comparada
  ao longo do tempo e com o mercado.
- **Mostra a experiência de ponta a ponta.** O NPS junta numa nota só tudo o que aconteceu: compra,
  entrega e atendimento. Por isso serve para cobrar várias áreas ao mesmo tempo.

### Quais áreas poderiam se beneficiar desses insights?

| Área | Como usa os insights |
|---|---|
| **Logística** | O atraso é o fator que mais derruba a nota. Metas de atraso máximo, escolha e cobrança de transportadoras, prazo prometido realista |
| **Atendimento** | Contatos repetidos e tempo de resolução pesam na nota. Comunicação proativa, resolução no primeiro contato, fila prioritária para pedidos de risco |
| **Produto / Catálogo** | Reclamações pesam muito. Investigar a origem (descrição errada, defeito, embalagem) |
| **Pricing / Comercial** | Desconto, frete e parcelamento **não** mudam a nota. Evita gastar margem para "comprar" satisfação |
| **CRM / Marketing** | Convidar potenciais promotores para avaliações e indicação; recuperar clientes de risco antes que virem detratores |
| **Estratégia / Diretoria** | Priorizar investimentos pelo ganho estimado em nota e definir metas por área |
| **Financeiro** | Orçamento de compensações (cupons, frete grátis) direcionado só a quem tem risco alto |

### Reflexão: como o NPS impacta...

**Recompra.** Promotores voltam a comprar e detratores não, e a base mostra isso de forma extrema:
taxa de recompra em 30 dias de **100% entre promotores, 38% entre neutros e 0% entre detratores**.
Cada cliente que passa de detrator a promotor é receita recorrente que não precisa de novo
investimento em aquisição. No sentido contrário, um NPS baixo é aviso de perda de clientes antes que
ela apareça no faturamento.

**Boca a boca.** No e-commerce o boca a boca é digital, público e cumulativo. O promotor recomenda
para amigos e deixa avaliação positiva, o que vira prova social para novos compradores. O detrator
reclama em canais públicos (Reclame Aqui, redes sociais, avaliações no marketplace), e essa
reclamação fica visível para todo cliente em potencial que pesquisar a loja. Com NPS -80, a empresa
tem muito mais gente falando mal do que bem dela.

**Market share.** O NPS da empresa em relação ao dos concorrentes ajuda a explicar quem ganha e quem
perde participação. Essa é a tese original do indicador (Frederick Reichheld, *The One Number You
Need to Grow*, Harvard Business Review, 2003). A empresa com mais promotores cresce de forma
orgânica, por recompra e indicação, com custo de aquisição menor; a empresa com mais detratores
precisa gastar mais com mídia só para repor os clientes que perde. No e-commerce, em que preço e
sortimento são fáceis de copiar, a experiência de entrega e atendimento é um dos poucos
diferenciais que se sustentam.

### Indicadores de mercado que complementariam a análise

| Indicador | Por que ajuda |
|---|---|
| **Benchmark de NPS do setor** (varejo online, por categoria) | Diz se -80 é um problema da empresa ou do setor inteiro, e define uma meta realista |
| **SLA logístico do mercado**: % de entregas no prazo (OTD), prazo médio por região, prazo dos concorrentes | Mostra se o prazo prometido é competitivo e se o atraso está acima do padrão |
| **Reputação pública**: nota e índice de solução no Reclame Aqui, nota nos marketplaces | Mede o efeito do boca a boca negativo e permite comparar com concorrentes |
| **Indicadores de atendimento**: resolução no primeiro contato (FCR), tempo médio de atendimento, Customer Effort Score (CES) | Explicam por que contatos repetidos derrubam a nota |
| **Taxa de recompra e churn do setor** | Traduz NPS em receita e mostra se a retenção está acima ou abaixo do mercado |
| **Market share e custo de aquisição (CAC)**: relatórios setoriais como os da ABComm e da NielsenIQ Ebit (Webshoppers) | Liga satisfação a crescimento e mostra o custo de repor clientes perdidos |
| **Taxa de devolução e troca** | Complementa as reclamações para entender problemas de produto |

---

## 2. Definição da target

### Qual variável representa a satisfação do cliente?

**`nps_score`**: a nota de 0 a 10 que o cliente dá à pergunta "o quanto você recomendaria a
empresa?". A partir dela derivamos:

- a **categoria NPS** de cada cliente: detrator (`nps_score < 7`), neutro
  (`7 <= nps_score < 9`) ou promotor (`nps_score >= 9`);
- o **NPS da empresa** (indicador agregado): % de promotores menos % de detratores, de -100 a +100.
  Na base: **-80**.

### Por que ela foi escolhida?

- É a **medida de satisfação e lealdade que a empresa já acompanha** e sobre a qual o problema foi
  formulado ("alta variabilidade do NPS").
- Representa o **resultado final da jornada inteira** (compra, entrega e atendimento), e não de uma
  etapa isolada.
- Tem **ligação comprovada com o comportamento que importa para o negócio**: a recompra (100% dos
  promotores contra 0% dos detratores).

As alternativas foram descartadas como target:

- **`csat_internal_score`**: é um score interno cuja metodologia não está descrita. A análise mostra
  que ele mede principalmente o **atendimento** (correlação de -0,74 com o tempo de resolução) e não
  a experiência completa.
- **`repeat_purchase_30d`**: é um **comportamento**, não uma opinião, e só é conhecido 30 dias
  depois. Serviria de target para outro problema (prever churn ou recompra), não para prever
  satisfação.

### Em que momento da jornada essa informação é coletada?

**Depois do encerramento da jornada de compra**, ou seja, depois da entrega e de eventuais contatos
com o atendimento. Isso define a regra do modelo: **só pode usar como entrada o que já é conhecido
antes desse momento**. Pela ordem dos acontecimentos:

```
compra -> entrega -> atendimento -> [PREVISÃO] -> pesquisa NPS -> CSAT interno -> recompra (30 dias)
```

### Existe algum risco de usar essa variável de forma inadequada?

Sim, vários:

1. **Vazamento de informação.** Usar como entrada do modelo variáveis que só existem depois da
   pesquisa (CSAT, recompra) faz o modelo parecer melhor do que é. No notebook 03 o R² sobe de 0,565
   para 0,650 com elas, mas esse modelo não funcionaria na prática.
2. **Viés de resposta.** Só quem responde à pesquisa tem nota. Clientes muito satisfeitos ou muito
   irritados costumam responder mais; os indiferentes, menos. A base pode não representar todos os
   clientes.
3. **Escala da nota.** Na pesquisa clássica a nota é um número inteiro; nesta base 83% das notas têm
   casa decimal. É preciso confirmar como ela é calculada. A classificação não arredonda a nota:
   `nps_score < 7` é detrator, `7 <= nps_score < 9` é neutro e `nps_score >= 9` é promotor.
4. **Confundir nota individual com o NPS.** O NPS é um indicador de **grupo**. Tirar conclusões a
   partir de grupos pequenos (por exemplo, os 3 pedidos com 8 dias de atraso) leva a erro.
5. **Manipulação do indicador (lei de Goodhart).** Se o NPS virar meta com bônus, surgem atalhos:
   pedir nota 10 ao cliente ou **deixar de enviar a pesquisa para quem o modelo prevê como
   detrator**. O NPS melhora no papel e piora na realidade. O modelo preditivo nunca deve ser usado
   para escolher quem recebe a pesquisa.
6. **Confundir correlação com causa.** A nota mostra **associação** com atraso e atendimento. O
   ganho real de uma ação precisa ser medido com teste controlado (grupo com ação x grupo sem ação).
7. **Usar a nota para avaliar pessoas.** Responsabilizar um atendente pela nota de um cliente que
   recebeu o pedido com 5 dias de atraso é injusto: a nota mistura fatores de várias áreas.
