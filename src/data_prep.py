"""Tratamento e preparação da base de NPS.

Etapas:
1. leitura do CSV bruto;
2. validação de esquema (todas as colunas do dicionário de dados estão presentes?);
3. diagnóstico de qualidade (nulos, duplicados, valores fora da faixa possível);
4. regras de consistência entre colunas (ex.: atraso maior que o prazo total);
5. limpeza: remove apenas o que é impossível de usar e SINALIZA o que é suspeito;
6. criação de colunas de apoio para a análise (categoria NPS, faixas de atraso etc.);
7. gravação da base tratada em data/processed/.

Uso:
    python -m src.data_prep
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src import config

# Faixa de valores fisicamente possíveis para cada coluna (mínimo, máximo).
# None significa "sem limite". Linhas fora dessas faixas são erro de registro e saem da base.
VALID_RANGES = {
    "customer_age": (16, 110),
    "customer_tenure_months": (0, None),
    "order_value": (0, None),
    "items_quantity": (1, None),
    "discount_value": (0, None),
    "payment_installments": (1, 24),
    "delivery_time_days": (0, None),
    "delivery_delay_days": (0, None),
    "freight_value": (0, None),
    "delivery_attempts": (1, None),
    "customer_service_contacts": (0, None),
    "resolution_time_days": (0, None),
    "complaints_count": (0, None),
    "repeat_purchase_30d": (0, 1),
    "csat_internal_score": (0, 10),
    "nps_score": (config.NPS_MIN, config.NPS_MAX),
}

# Regras de consistência entre colunas. Cada regra devolve True quando a linha é suspeita.
# Essas linhas NÃO são removidas: viram colunas "flag_*" para que o impacto possa ser
# medido (análise de sensibilidade no notebook 01).
CONSISTENCY_RULES = {
    "flag_delay_exceeds_delivery_time": (
        "Atraso maior que o prazo total de entrega",
        lambda df: df["delivery_delay_days"] > df["delivery_time_days"],
    ),
    "flag_discount_exceeds_order_value": (
        "Desconto maior ou igual ao valor do pedido",
        lambda df: df["discount_value"] >= df["order_value"],
    ),
    "flag_tenure_exceeds_adult_life": (
        "Tempo de casa maior que a vida adulta do cliente",
        lambda df: df["customer_tenure_months"]
        > (df["customer_age"] - 18).clip(lower=0) * 12,
    ),
}

# Pontos de atenção de semântica: não são erro, mas pedem confirmação com o negócio.
ATTENTION_RULES = {
    "flag_complaint_without_contact": (
        "Reclamação registrada sem contato com o atendimento",
        lambda df: (df["complaints_count"] > 0)
        & (df["customer_service_contacts"] == 0),
    ),
    "flag_resolution_without_contact": (
        "Tempo de resolução registrado sem contato com o atendimento",
        lambda df: (df["resolution_time_days"] > 0)
        & (df["customer_service_contacts"] == 0),
    ),
}

# Faixas usadas na análise exploratória. Os cortes de atraso, reclamações e contatos
# foram definidos a partir dos pontos de mudança observados na análise de negócio.
RANGE_DEFINITIONS = {
    "delay_range": (
        "delivery_delay_days",
        [-np.inf, 0, 2, 3, np.inf],
        ["No prazo", "1 a 2 dias", "3 dias", "4 dias ou mais"],
    ),
    "complaints_range": (
        "complaints_count",
        [-np.inf, 1, 2, 4, np.inf],
        ["0 a 1", "2", "3 a 4", "5 ou mais"],
    ),
    "contacts_range": (
        "customer_service_contacts",
        [-np.inf, 0, 1, 2, np.inf],
        ["Nenhum", "1", "2", "3 ou mais"],
    ),
    "resolution_range": (
        "resolution_time_days",
        [-np.inf, 2, 5, 8, np.inf],
        ["Até 2 dias", "3 a 5 dias", "6 a 8 dias", "9 dias ou mais"],
    ),
    "delivery_time_range": (
        "delivery_time_days",
        [-np.inf, 4, 7, 10, np.inf],
        ["Até 4 dias", "5 a 7 dias", "8 a 10 dias", "11 dias ou mais"],
    ),
    "age_range": (
        "customer_age",
        [-np.inf, 25, 35, 45, 55, np.inf],
        ["Até 25", "26 a 35", "36 a 45", "46 a 55", "56 ou mais"],
    ),
    "tenure_range": (
        "customer_tenure_months",
        [-np.inf, 12, 36, 60, np.inf],
        ["Até 1 ano", "1 a 3 anos", "3 a 5 anos", "Mais de 5 anos"],
    ),
    "order_value_range": (
        "order_value",
        [-np.inf, 200, 400, 700, np.inf],
        ["Até R$ 200", "R$ 200 a 400", "R$ 400 a 700", "Acima de R$ 700"],
    ),
    "installments_range": (
        "payment_installments",
        [-np.inf, 1, 3, 6, np.inf],
        ["À vista", "2 a 3x", "4 a 6x", "7x ou mais"],
    ),
}

EXPERIENCE_ORDER = ["Boa", "Intermediária", "Ruim"]


# --------------------------------------------------------------------------------------
# Leitura e diagnóstico
# --------------------------------------------------------------------------------------
def load_raw_data(path=config.DATA_RAW_PATH) -> pd.DataFrame:
    """Lê o CSV bruto exatamente como veio do repositório do curso."""
    return pd.read_csv(path, encoding="utf-8")


def validate_schema(df: pd.DataFrame) -> None:
    """Interrompe o processo se faltar alguma coluna prevista no dicionário de dados."""
    missing_columns = sorted(set(config.EXPECTED_COLUMNS) - set(df.columns))
    if missing_columns:
        raise ValueError(f"Colunas ausentes na base: {missing_columns}")


def quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """Resumo por coluna: tipo, nulos, valores distintos, mínimo e máximo."""
    numeric = df.select_dtypes("number")
    report = pd.DataFrame(
        {
            "tipo": df.dtypes.astype(str),
            "nulos": df.isna().sum(),
            "pct_nulos": (df.isna().mean() * 100).round(2),
            "valores_distintos": df.nunique(),
            "minimo": numeric.min(),
            "maximo": numeric.max(),
        }
    )
    report.index.name = "coluna"
    return report


def find_range_violations(df: pd.DataFrame) -> pd.DataFrame:
    """Marca, coluna a coluna, os valores fora da faixa possível (True = inválido)."""
    violations = pd.DataFrame(False, index=df.index, columns=list(VALID_RANGES))
    for column, (lower, upper) in VALID_RANGES.items():
        if lower is not None:
            violations[column] |= df[column] < lower
        if upper is not None:
            violations[column] |= df[column] > upper
    return violations


def consistency_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Quantas linhas caem em cada regra de consistência e de atenção."""
    rows = []
    for rule_type, rules in (
        ("inconsistência", CONSISTENCY_RULES),
        ("ponto de atenção", ATTENTION_RULES),
    ):
        for flag_name, (description, rule) in rules.items():
            mask = rule(df)
            rows.append(
                {
                    "regra": description,
                    "tipo": rule_type,
                    "coluna_flag": flag_name,
                    "linhas": int(mask.sum()),
                    "pct_linhas": round(mask.mean() * 100, 1),
                }
            )
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------------------
# Limpeza
# --------------------------------------------------------------------------------------
def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Limpa a base e devolve (base_limpa, log_da_limpeza).

    Critério: só sai da base o que não pode ser usado de jeito nenhum
    (duplicado, sem nota de NPS, valor impossível). O que é apenas suspeito fica
    na base com uma flag, para não jogar fora informação sem medir o efeito.
    """
    cleaning_log = {"linhas_iniciais": len(df)}
    clean_df = df.copy()

    # Padroniza texto da região (espaços extras e caixa)
    clean_df["customer_region"] = (
        clean_df["customer_region"].astype("string").str.strip().str.title()
    )

    # 1) Duplicados: linha inteira repetida e pedido repetido
    before = len(clean_df)
    clean_df = clean_df.drop_duplicates()
    clean_df = clean_df.drop_duplicates(subset="order_id", keep="first")
    cleaning_log["removidas_duplicadas"] = before - len(clean_df)

    # 2) Sem target não há o que aprender nem analisar
    before = len(clean_df)
    clean_df = clean_df.dropna(subset=[config.TARGET_COLUMN])
    cleaning_log["removidas_sem_nps"] = before - len(clean_df)

    # 3) Valores impossíveis (ex.: nota 11, idade negativa)
    before = len(clean_df)
    invalid_rows = find_range_violations(clean_df).any(axis=1)
    clean_df = clean_df.loc[~invalid_rows]
    cleaning_log["removidas_valor_impossivel"] = before - len(clean_df)

    # 4) Sinaliza inconsistências e pontos de atenção (as linhas permanecem)
    for flag_name, (_, rule) in {**CONSISTENCY_RULES, **ATTENTION_RULES}.items():
        clean_df[flag_name] = rule(clean_df).astype(int)
    clean_df["has_inconsistency"] = (
        clean_df[list(CONSISTENCY_RULES)].any(axis=1).astype(int)
    )

    # Nulos nas variáveis de entrada NÃO são preenchidos aqui: o preenchimento fica dentro
    # do pipeline do modelo (SimpleImputer), aprendido só com os dados de treino.
    cleaning_log["linhas_finais"] = len(clean_df)
    cleaning_log["linhas_sinalizadas_inconsistentes"] = int(
        clean_df["has_inconsistency"].sum()
    )
    return clean_df.reset_index(drop=True), cleaning_log


# --------------------------------------------------------------------------------------
# Colunas de apoio para a análise
# --------------------------------------------------------------------------------------
def classify_nps(scores: pd.Series) -> pd.Series:
    """Converte a nota (0 a 10) na categoria clássica do NPS."""
    categories = np.select(
        [scores >= config.PROMOTER_LIMIT, scores >= config.DETRACTOR_LIMIT],
        ["promotor", "neutro"],
        default="detrator",
    )
    return pd.Series(
        pd.Categorical(categories, categories=config.NPS_CATEGORY_ORDER, ordered=True),
        index=scores.index,
        name="nps_category",
    )


def nps_index(scores: pd.Series) -> float:
    """NPS clássico: % de promotores menos % de detratores (vai de -100 a +100)."""
    scores = pd.Series(scores).dropna()
    promoters = (scores >= config.PROMOTER_LIMIT).mean()
    detractors = (scores < config.DETRACTOR_LIMIT).mean()
    return round((promoters - detractors) * 100, 1)


def classify_experience(df: pd.DataFrame) -> pd.Series:
    """Agrupa os pedidos pela experiência vivida, usando os pontos de ruptura da EDA.

    - Boa: até 1 dia de atraso, até 2 reclamações e no máximo 1 contato com o atendimento;
    - Ruim: 3 dias ou mais de atraso OU 5 reclamações ou mais;
    - Intermediária: todo o resto.
    """
    good = (
        (df["delivery_delay_days"] <= 1)
        & (df["complaints_count"] <= 2)
        & (df["customer_service_contacts"] <= 1)
    )
    bad = (df["delivery_delay_days"] >= 3) | (df["complaints_count"] >= 5)
    experience = np.select([good, bad], ["Boa", "Ruim"], default="Intermediária")
    return pd.Series(
        pd.Categorical(experience, categories=EXPERIENCE_ORDER, ordered=True),
        index=df.index,
        name="experience_profile",
    )


def add_analysis_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Cria as colunas derivadas usadas na EDA (não entram no modelo)."""
    enriched = df.copy()
    enriched["nps_category"] = classify_nps(enriched[config.TARGET_COLUMN])
    enriched["is_detractor"] = (enriched["nps_category"] == "detrator").astype(int)
    enriched["is_promoter"] = (enriched["nps_category"] == "promotor").astype(int)
    enriched["on_time"] = (enriched["delivery_delay_days"] == 0).astype(int)
    enriched["net_order_value"] = enriched["order_value"] - enriched["discount_value"]
    enriched["discount_pct"] = (
        enriched["discount_value"] / enriched["order_value"] * 100
    ).round(1)

    for range_column, (source_column, bins, labels) in RANGE_DEFINITIONS.items():
        enriched[range_column] = pd.cut(
            enriched[source_column], bins=bins, labels=labels, ordered=True
        )

    enriched["experience_profile"] = classify_experience(enriched)
    return enriched


def restore_category_order(df: pd.DataFrame) -> pd.DataFrame:
    """Reaplica a ordem das categorias depois de ler o CSV (o CSV não guarda a ordem)."""
    restored = df.copy()
    restored["nps_category"] = pd.Categorical(
        restored["nps_category"], categories=config.NPS_CATEGORY_ORDER, ordered=True
    )
    for range_column, (_, _, labels) in RANGE_DEFINITIONS.items():
        restored[range_column] = pd.Categorical(
            restored[range_column], categories=labels, ordered=True
        )
    restored["experience_profile"] = pd.Categorical(
        restored["experience_profile"], categories=EXPERIENCE_ORDER, ordered=True
    )
    return restored


def load_processed_data(path=config.DATA_PROCESSED_PATH) -> pd.DataFrame:
    """Lê a base tratada já com as categorias na ordem certa."""
    return restore_category_order(pd.read_csv(path, encoding="utf-8"))


def drop_leakage_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remove do conjunto de modelagem as variáveis indisponíveis no momento previsto."""
    leakage_features = set(config.LEAKAGE_COLUMNS)
    configured_features = set(config.MODEL_FEATURES)
    overlap = leakage_features & configured_features
    if overlap:
        raise ValueError(
            f"Variáveis com vazamento configuradas como preditoras: {sorted(overlap)}"
        )
    missing_columns = leakage_features - set(df.columns)
    if missing_columns:
        raise ValueError(
            "Não foi possível remover variáveis com vazamento ausentes da base: "
            f"{sorted(missing_columns)}"
        )
    return df.drop(columns=config.LEAKAGE_COLUMNS)


# --------------------------------------------------------------------------------------
# Execução completa
# --------------------------------------------------------------------------------------
def run_data_preparation(save: bool = True) -> tuple[pd.DataFrame, dict]:
    """Executa todas as etapas e (opcionalmente) grava a base tratada."""
    raw_df = load_raw_data()
    validate_schema(raw_df)
    clean_df, cleaning_log = clean_data(raw_df)
    processed_df = add_analysis_columns(clean_df)

    if save:
        config.DATA_PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
        processed_df.to_csv(config.DATA_PROCESSED_PATH, index=False, encoding="utf-8")
    return processed_df, cleaning_log


def main() -> None:
    """Executa a preparação da base pela linha de comando."""
    config.use_utf8_output()
    processed_df, cleaning_log = run_data_preparation(save=True)

    print("Tratamento concluído")
    for step, value in cleaning_log.items():
        print(f"  {step}: {value}")
    print(f"  NPS da base: {nps_index(processed_df[config.TARGET_COLUMN])}")
    print(
        f"  Base tratada salva em: {config.DATA_PROCESSED_PATH.relative_to(config.PROJECT_ROOT)}"
    )


if __name__ == "__main__":
    main()
