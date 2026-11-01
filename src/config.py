"""Configurações centrais do projeto: caminhos, grupos de colunas e regras do NPS.

Tudo que é "decisão de projeto" (quais colunas entram no modelo, onde ficam os
arquivos, qual semente aleatória usar) fica concentrado aqui, para que notebooks e
scripts usem exatamente as mesmas definições.
"""

import sys
from pathlib import Path

# --------------------------------------------------------------------------------------
# Caminhos
# --------------------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_RAW_PATH = PROJECT_ROOT / "data" / "raw" / "desafio_nps_fase_1.csv"
DATA_PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "nps_tratado.csv"

MODELS_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODELS_DIR / "nps_regressor.joblib"
METRICS_PATH = MODELS_DIR / "metrics.json"

REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
PRIORITIZED_ORDERS_PATH = REPORTS_DIR / "pedidos_priorizados.csv"

# --------------------------------------------------------------------------------------
# Reprodutibilidade
# --------------------------------------------------------------------------------------
RANDOM_STATE = 42
TEST_SIZE = 0.20
CV_FOLDS = 5

# --------------------------------------------------------------------------------------
# Variável alvo e regra clássica do NPS
# --------------------------------------------------------------------------------------
TARGET_COLUMN = "nps_score"
NPS_MIN, NPS_MAX = 0.0, 10.0

# A nota é contínua: < 7 é detrator, de 7 a < 9 é neutro e >= 9 é promotor.
# Assim, 6.9 continua sendo detrator, sem arredondar a nota.
DETRACTOR_LIMIT = 7.0  # nota < 7  -> detrator
PROMOTER_LIMIT = 9.0  # nota >= 9 -> promotor
NPS_CATEGORY_ORDER = ["detrator", "neutro", "promotor"]

# --------------------------------------------------------------------------------------
# Grupos de colunas (segue o dicionário de dados do desafio)
# --------------------------------------------------------------------------------------
ID_COLUMNS = ["customer_id", "order_id"]
CUSTOMER_COLUMNS = ["customer_age", "customer_region", "customer_tenure_months"]
ORDER_COLUMNS = [
    "order_value",
    "items_quantity",
    "discount_value",
    "payment_installments",
]
LOGISTICS_COLUMNS = [
    "delivery_time_days",
    "delivery_delay_days",
    "freight_value",
    "delivery_attempts",
]
SERVICE_COLUMNS = [
    "customer_service_contacts",
    "resolution_time_days",
    "complaints_count",
]

# Colunas que NÃO podem entrar no modelo porque nascem junto ou depois da própria
# pesquisa de NPS (vazamento de informação):
# - csat_internal_score: é outra pesquisa de satisfação, ou seja, uma "irmã" da target;
# - repeat_purchase_30d: só é conhecida 30 dias depois do pedido, é consequência
#   da satisfação e não causa.
LEAKAGE_COLUMNS = ["csat_internal_score", "repeat_purchase_30d"]

EXPECTED_COLUMNS = (
    ID_COLUMNS
    + CUSTOMER_COLUMNS
    + ORDER_COLUMNS
    + LOGISTICS_COLUMNS
    + SERVICE_COLUMNS
    + LEAKAGE_COLUMNS
    + [TARGET_COLUMN]
)

# Variáveis de entrada do modelo: tudo que a empresa já sabe ANTES de enviar a pesquisa.
CATEGORICAL_FEATURES = ["customer_region"]
NUMERIC_FEATURES = [
    column
    for column in CUSTOMER_COLUMNS + ORDER_COLUMNS + LOGISTICS_COLUMNS + SERVICE_COLUMNS
    if column not in CATEGORICAL_FEATURES
]
MODEL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

# Os quatro fatores operacionais que a análise exploratória apontou como decisivos.
# São usados para explicar cada previsão ("o que está puxando a nota para baixo").
OPERATIONAL_DRIVERS = [
    "delivery_delay_days",
    "complaints_count",
    "customer_service_contacts",
    "resolution_time_days",
]

# --------------------------------------------------------------------------------------
# Rótulos em português para gráficos e relatórios
# --------------------------------------------------------------------------------------
FEATURE_LABELS = {
    "customer_id": "ID do cliente",
    "order_id": "ID do pedido",
    "customer_age": "Idade do cliente",
    "customer_region": "Região",
    "customer_tenure_months": "Tempo de casa (meses)",
    "order_value": "Valor do pedido (R$)",
    "items_quantity": "Quantidade de itens",
    "discount_value": "Desconto (R$)",
    "payment_installments": "Parcelas",
    "delivery_time_days": "Prazo total de entrega (dias)",
    "delivery_delay_days": "Dias de atraso",
    "freight_value": "Frete (R$)",
    "delivery_attempts": "Tentativas de entrega",
    "customer_service_contacts": "Contatos com o atendimento",
    "resolution_time_days": "Tempo de resolução (dias)",
    "complaints_count": "Reclamações",
    "csat_internal_score": "CSAT interno",
    "repeat_purchase_30d": "Recompra em 30 dias",
    "nps_score": "Nota NPS",
}

FEATURE_AREAS = {
    **{column: "Cliente" for column in CUSTOMER_COLUMNS},
    **{column: "Pedido" for column in ORDER_COLUMNS},
    **{column: "Logística" for column in LOGISTICS_COLUMNS},
    **{column: "Atendimento" for column in SERVICE_COLUMNS},
    **{column: "Pós-pesquisa (vazamento)" for column in LEAKAGE_COLUMNS},
}

# Área da empresa responsável por agir em cada fator operacional
DRIVER_OWNERS = {
    "delivery_delay_days": "Logística",
    "complaints_count": "Atendimento / Produto",
    "customer_service_contacts": "Atendimento",
    "resolution_time_days": "Atendimento",
}


def use_utf8_output() -> None:
    """Força UTF-8 no terminal.

    No Windows o Python usa cp1252 por padrão quando a saída é redirecionada, o que
    quebra a impressão de acentos. Os scripts chamam esta função logo no início.
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
