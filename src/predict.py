"""Uso prático do modelo: gera a lista de pedidos priorizados por risco de detração.

Recebe um CSV de pedidos (mesmas colunas da base original; a nota de NPS NÃO é
necessária) e devolve, para cada pedido:
- a nota de NPS prevista e a categoria correspondente;
- a faixa de risco e a ação recomendada;
- o fator operacional que mais está derrubando a nota e a área responsável.

Uso:
    python -m src.predict
    python -m src.predict --input caminho/pedidos.csv --output caminho/saida.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.pipeline import Pipeline

from src import config
from src.data_prep import classify_nps
from src.modeling import (
    assign_risk_tier,
    main_negative_driver,
    predict_nps,
    recommended_action,
    unit_impacts,
)


def load_model(path: Path = config.MODEL_PATH) -> Pipeline:
    """Carrega o pipeline treinado (preparação + modelo)."""
    if not path.exists():
        raise FileNotFoundError(
            f"Modelo não encontrado em {path}. Rode antes: python -m src.train_model"
        )
    return joblib.load(path)


def score_orders(orders: pd.DataFrame, model: Pipeline) -> pd.DataFrame:
    """Aplica o modelo e monta a tabela de priorização, do pedido mais crítico ao menos."""
    missing_columns = sorted(set(config.MODEL_FEATURES) - set(orders.columns))
    if missing_columns:
        raise ValueError(f"Colunas necessárias ausentes: {missing_columns}")

    X = orders[config.MODEL_FEATURES]
    predicted_scores = pd.Series(predict_nps(model, X), index=orders.index)
    risk_tier = assign_risk_tier(predicted_scores)
    risk_tier.index = orders.index
    driver_column = main_negative_driver(X, unit_impacts(model))

    id_columns = [column for column in config.ID_COLUMNS if column in orders.columns]
    scored = orders[id_columns + config.OPERATIONAL_DRIVERS].copy()
    scored["predicted_nps"] = predicted_scores.round(1)
    scored["predicted_category"] = classify_nps(predicted_scores)
    scored["risk_tier"] = risk_tier
    scored["main_driver"] = driver_column.map(config.FEATURE_LABELS).fillna(
        "Nenhum problema operacional"
    )
    scored["driver_owner"] = driver_column.map(config.DRIVER_OWNERS).fillna("-")
    scored["recommended_action"] = recommended_action(risk_tier)
    return scored.sort_values("predicted_nps").reset_index(drop=True)


def parse_arguments() -> argparse.Namespace:
    """Interpreta os argumentos de entrada e saída do preditor."""
    parser = argparse.ArgumentParser(
        description="Prioriza pedidos pelo risco de virar detrator."
    )
    parser.add_argument(
        "--input", type=Path, default=config.DATA_RAW_PATH, help="CSV de pedidos"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=config.PRIORITIZED_ORDERS_PATH,
        help="CSV de saída",
    )
    return parser.parse_args()


def main() -> None:
    """Lê pedidos, aplica o modelo e apresenta o semáforo de risco."""
    config.use_utf8_output()
    arguments = parse_arguments()

    orders = pd.read_csv(arguments.input, encoding="utf-8")
    scored = score_orders(orders, load_model())

    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    scored.to_csv(arguments.output, index=False, encoding="utf-8")

    summary = scored.groupby("risk_tier", observed=False).agg(
        pedidos=("predicted_nps", "size"), nota_prevista_media=("predicted_nps", "mean")
    )
    summary["pct_pedidos"] = summary["pedidos"] / summary["pedidos"].sum() * 100
    print("Pedidos por faixa de risco")
    print(summary.round(1).to_string())
    print("\nFator que mais derruba a nota (pedidos em risco Crítico ou Alto)")
    at_risk = scored[scored["risk_tier"].isin(["Crítico", "Alto"])]
    print(at_risk["main_driver"].value_counts().to_string())
    print(f"\nLista priorizada salva em: {arguments.output}")


if __name__ == "__main__":
    main()
