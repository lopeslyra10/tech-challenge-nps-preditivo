"""Funções de modelagem: separação dos dados, pipelines, comparação, avaliação e uso.

A estratégia adotada (justificada no notebook 03):
- modelo principal de REGRESSÃO, que prevê a nota de 0 a 10;
- a nota prevista é traduzida em categoria NPS e em faixa de risco com ação recomendada;
- um modelo de CLASSIFICAÇÃO (detrator x não detrator) é treinado só como comparação.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    mean_absolute_error,
    r2_score,
    roc_auc_score,
    root_mean_squared_error,
)
from sklearn.model_selection import (
    KFold,
    StratifiedKFold,
    cross_validate,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src import config
from src.data_prep import classify_nps

# Faixas de risco a partir da nota prevista: (limite superior, nome, ação recomendada).
# Os cortes seguem a régua do NPS e foram conferidos no conjunto de teste (notebook 03).
RISK_TIERS = [
    (
        3.0,
        "Crítico",
        "Contato proativo antes da pesquisa, pedido de desculpas e compensação "
        "(cupom ou frete grátis na próxima compra); chamado aberto vai para a fila prioritária.",
    ),
    (
        5.0,
        "Alto",
        "Avisar o cliente sobre o status da entrega antes que ele pergunte e acompanhar "
        "o chamado até o fim.",
    ),
    (
        7.0,
        "Atenção",
        "Monitorar o pedido; mensagem de acompanhamento após a entrega.",
    ),
    (
        np.inf,
        "Potencial promotor",
        "Enviar a pesquisa no melhor momento e convidar para avaliação ou programa de indicação.",
    ),
]
RISK_TIER_ORDER = [name for _, name, _ in RISK_TIERS]

# Um fator só é apontado como "principal problema" do pedido se tirar pelo menos
# meio ponto da nota prevista; abaixo disso é ruído (ex.: 1 dia de resolução).
MIN_DRIVER_IMPACT = 0.5


# --------------------------------------------------------------------------------------
# Dados de entrada
# --------------------------------------------------------------------------------------
def get_features_and_target(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Separa as variáveis de entrada (X) da nota de NPS (y)."""
    return df[config.MODEL_FEATURES].copy(), df[config.TARGET_COLUMN].copy()


def split_train_test(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separa 80% treino / 20% teste, estratificando pela categoria NPS.

    A estratificação garante que os promotores (só ~4% da base) apareçam nas duas
    partes na mesma proporção. O teste fica guardado e só é usado na avaliação final.
    """
    strata = classify_nps(df[config.TARGET_COLUMN])
    train_df, test_df = train_test_split(
        df,
        test_size=config.TEST_SIZE,
        random_state=config.RANDOM_STATE,
        stratify=strata,
    )
    return train_df.copy(), test_df.copy()


# --------------------------------------------------------------------------------------
# Pipelines
# --------------------------------------------------------------------------------------
def build_preprocessor() -> ColumnTransformer:
    """Preparação das variáveis, aprendida só com os dados de treino.

    - numéricas: preenche nulos com a mediana e padroniza (média 0, desvio 1),
      necessário para modelos lineares compararem variáveis de escalas diferentes;
    - região: one-hot encoding, descartando a primeira categoria para evitar
      colinearidade perfeita na regressão linear.
    """
    numeric_pipeline = Pipeline(
        [("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]
    )
    categorical_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(drop="first", handle_unknown="ignore")),
        ]
    )
    return ColumnTransformer(
        [
            ("num", numeric_pipeline, config.NUMERIC_FEATURES),
            ("cat", categorical_pipeline, config.CATEGORICAL_FEATURES),
        ]
    )


def make_pipeline(estimator) -> Pipeline:
    """Junta preparação + modelo num único objeto (evita vazamento na validação cruzada)."""
    return Pipeline([("preprocessor", build_preprocessor()), ("model", estimator)])


def regression_candidates() -> dict:
    """Modelos de regressão comparados, do mais simples ao mais complexo."""
    return {
        "Baseline (média)": DummyRegressor(strategy="mean"),
        "Regressão Linear": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=300,
            min_samples_leaf=5,
            random_state=config.RANDOM_STATE,
            n_jobs=-1,
        ),
        "Gradient Boosting": HistGradientBoostingRegressor(
            learning_rate=0.05, max_iter=300, random_state=config.RANDOM_STATE
        ),
    }


def classification_candidates() -> dict:
    """Modelos de classificação (detrator = 1) usados como comparação."""
    return {
        "Baseline (proporção)": DummyClassifier(strategy="prior"),
        "Regressão Logística": LogisticRegression(max_iter=1000),
        "Random Forest": RandomForestClassifier(
            n_estimators=300,
            min_samples_leaf=5,
            random_state=config.RANDOM_STATE,
            n_jobs=-1,
        ),
        "Gradient Boosting": HistGradientBoostingClassifier(
            learning_rate=0.05, max_iter=300, random_state=config.RANDOM_STATE
        ),
    }


# --------------------------------------------------------------------------------------
# Comparação por validação cruzada (só com o treino)
# --------------------------------------------------------------------------------------
def compare_regressors(X_train: pd.DataFrame, y_train: pd.Series) -> pd.DataFrame:
    """Validação cruzada em 5 partes. Métrica principal: MAE (erro médio em pontos de nota)."""
    folds = KFold(
        n_splits=config.CV_FOLDS, shuffle=True, random_state=config.RANDOM_STATE
    )
    scoring = {
        "MAE": "neg_mean_absolute_error",
        "RMSE": "neg_root_mean_squared_error",
        "R2": "r2",
    }
    rows = []
    for name, estimator in regression_candidates().items():
        scores = cross_validate(
            make_pipeline(estimator), X_train, y_train, cv=folds, scoring=scoring
        )
        rows.append(
            {
                "modelo": name,
                "MAE": -scores["test_MAE"].mean(),
                "MAE_desvio": scores["test_MAE"].std(),
                "RMSE": -scores["test_RMSE"].mean(),
                "R2": scores["test_R2"].mean(),
            }
        )
    return pd.DataFrame(rows).sort_values("MAE").reset_index(drop=True)


def compare_classifiers(
    X_train: pd.DataFrame, y_train_score: pd.Series
) -> pd.DataFrame:
    """Mesma comparação para a abordagem de classificação (alvo: é detrator?)."""
    y_detractor = (y_train_score < config.DETRACTOR_LIMIT).astype(int)
    folds = StratifiedKFold(
        n_splits=config.CV_FOLDS, shuffle=True, random_state=config.RANDOM_STATE
    )
    scoring = {
        "ROC_AUC": "roc_auc",
        "PR_AUC": "average_precision",
        "Acuracia_balanceada": "balanced_accuracy",
    }
    rows = []
    for name, estimator in classification_candidates().items():
        scores = cross_validate(
            make_pipeline(estimator), X_train, y_detractor, cv=folds, scoring=scoring
        )
        rows.append(
            {
                "modelo": name,
                **{metric: scores[f"test_{metric}"].mean() for metric in scoring},
            }
        )
    return (
        pd.DataFrame(rows)
        .sort_values("ROC_AUC", ascending=False)
        .reset_index(drop=True)
    )


# --------------------------------------------------------------------------------------
# Previsão e avaliação
# --------------------------------------------------------------------------------------
def predict_nps(model: Pipeline, X: pd.DataFrame) -> np.ndarray:
    """Nota prevista, limitada à escala da pesquisa (0 a 10).

    A regressão linear pode extrapolar (ex.: -1.5 para um pedido muito ruim); como a
    pesquisa não tem nota negativa, o valor é cortado nos limites da escala.
    """
    return np.clip(model.predict(X), config.NPS_MIN, config.NPS_MAX)


def regression_metrics(y_true: pd.Series, y_pred: np.ndarray) -> dict:
    """Métricas de regressão, todas na unidade da nota (pontos de 0 a 10)."""
    return {
        "MAE": round(float(mean_absolute_error(y_true, y_pred)), 3),
        "RMSE": round(float(root_mean_squared_error(y_true, y_pred)), 3),
        "R2": round(float(r2_score(y_true, y_pred)), 3),
    }


def detractor_ranking_metrics(y_true: pd.Series, y_pred_score: np.ndarray) -> dict:
    """Quão bem a nota prevista ordena os clientes por risco de virar detrator.

    ROC-AUC = chance de um detrator real receber nota prevista menor que um não detrator.
    0.5 é sorteio; 1.0 é ordenação perfeita.
    """
    is_detractor = (y_true < config.DETRACTOR_LIMIT).astype(int)
    risk_score = -np.asarray(y_pred_score)  # nota menor = risco maior
    return {
        "ROC_AUC": round(float(roc_auc_score(is_detractor, risk_score)), 3),
        "PR_AUC": round(float(average_precision_score(is_detractor, risk_score)), 3),
    }


def assign_risk_tier(predicted_scores) -> pd.Series:
    """Traduz a nota prevista na faixa de risco usada pela operação."""
    predicted_scores = np.asarray(predicted_scores)
    upper_limits = [upper for upper, _, _ in RISK_TIERS]
    positions = np.searchsorted(upper_limits, predicted_scores, side="right")
    names = np.array(RISK_TIER_ORDER)[np.minimum(positions, len(RISK_TIERS) - 1)]
    return pd.Series(
        pd.Categorical(names, categories=RISK_TIER_ORDER, ordered=True),
        name="risk_tier",
    )


def recommended_action(risk_tier: pd.Series) -> pd.Series:
    """Ação recomendada para cada faixa de risco."""
    actions = {name: action for _, name, action in RISK_TIERS}
    return risk_tier.astype(str).map(actions).rename("recommended_action")


def risk_tier_table(y_true: pd.Series, y_pred: np.ndarray) -> pd.DataFrame:
    """Para cada faixa de risco prevista: quantos pedidos e como eles realmente avaliaram."""
    table = pd.DataFrame(
        {
            "faixa_risco": assign_risk_tier(y_pred).values,
            "nota_real": np.asarray(y_true),
        }
    )
    summary = table.groupby("faixa_risco", observed=False).agg(
        pedidos=("nota_real", "size"),
        nota_real_media=("nota_real", "mean"),
        pct_detratores_reais=(
            "nota_real",
            lambda s: (s < config.DETRACTOR_LIMIT).mean() * 100,
        ),
        pct_promotores_reais=(
            "nota_real",
            lambda s: (s >= config.PROMOTER_LIMIT).mean() * 100,
        ),
    )
    summary["pct_pedidos"] = summary["pedidos"] / summary["pedidos"].sum() * 100
    return summary.round(1)


# --------------------------------------------------------------------------------------
# Interpretação
# --------------------------------------------------------------------------------------
def unit_impacts(model: Pipeline) -> pd.Series | None:
    """Quanto a nota prevista muda quando cada variável numérica aumenta 1 unidade.

    Só faz sentido para o modelo linear: o coeficiente aprendido sobre a variável
    padronizada é dividido pelo desvio-padrão, voltando para a unidade original
    (ex.: "cada dia de atraso tira 0.9 ponto"). Para outros modelos devolve None.
    """
    estimator = model.named_steps["model"]
    if not isinstance(estimator, LinearRegression):
        return None
    scaler = (
        model.named_steps["preprocessor"]
        .named_transformers_["num"]
        .named_steps["scaler"]
    )
    coefficients = estimator.coef_[: len(config.NUMERIC_FEATURES)]
    impacts = pd.Series(
        coefficients / scaler.scale_,
        index=config.NUMERIC_FEATURES,
        name="impacto_por_unidade",
    )
    return impacts.sort_values()


def main_negative_driver(X: pd.DataFrame, impacts: pd.Series | None) -> pd.Series:
    """Fator operacional que mais está puxando a nota de cada pedido para baixo.

    Contribuição = impacto por unidade x valor do pedido (ex.: 4 dias de atraso x -0.9).
    Comparar contra "zero" faz sentido aqui porque zero é o cenário ideal para os quatro
    fatores (nenhum atraso, nenhuma reclamação, nenhum contato, resolução imediata).

    Devolve o nome da coluna (ex.: "delivery_delay_days") ou None quando nenhum dos
    quatro fatores tira pelo menos MIN_DRIVER_IMPACT ponto da nota.
    """
    if impacts is None:
        return pd.Series(None, index=X.index, name="main_driver", dtype="object")
    contributions = X[config.OPERATIONAL_DRIVERS].mul(
        impacts[config.OPERATIONAL_DRIVERS]
    )
    driver_column = contributions.idxmin(axis=1).astype("object")
    no_problem = contributions.min(axis=1) > -MIN_DRIVER_IMPACT
    return driver_column.where(~no_problem, None).rename("main_driver")
