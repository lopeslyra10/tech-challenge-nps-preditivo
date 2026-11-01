"""Pipeline de treino do modelo preditivo de NPS.

Passos:
1. lê a base tratada (gerada por src.data_prep);
2. separa treino (80%) e teste (20%), estratificando pela categoria NPS;
3. compara modelos de regressão e de classificação por validação cruzada no treino;
4. escolhe o regressor de menor erro médio (MAE) e avalia uma única vez no teste;
5. re-treina o modelo escolhido com 100% da base e salva modelo + métricas.

Uso:
    python -m src.train_model
"""

from __future__ import annotations

import json
from datetime import date

import joblib
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.metrics import roc_auc_score

from src import config
from src.data_prep import drop_leakage_columns, load_processed_data
from src.modeling import (
    classification_candidates,
    compare_classifiers,
    compare_regressors,
    detractor_ranking_metrics,
    get_features_and_target,
    make_pipeline,
    predict_nps,
    regression_candidates,
    regression_metrics,
    risk_tier_table,
    split_train_test,
    unit_impacts,
)


def run_training(save: bool = True) -> dict:
    """Executa o pipeline completo e devolve tudo que foi calculado."""
    df = drop_leakage_columns(load_processed_data())
    train_df, test_df = split_train_test(df)
    X_train, y_train = get_features_and_target(train_df)
    X_test, y_test = get_features_and_target(test_df)

    # Seleção de modelo: só o treino participa (o teste continua "lacrado")
    regression_cv = compare_regressors(X_train, y_train)
    classification_cv = compare_classifiers(X_train, y_train)

    best_regressor_name = regression_cv.loc[0, "modelo"]
    model = make_pipeline(regression_candidates()[best_regressor_name]).fit(
        X_train, y_train
    )

    # Avaliação final no teste
    y_pred = predict_nps(model, X_test)
    baseline = make_pipeline(DummyRegressor(strategy="mean")).fit(X_train, y_train)
    baseline_metrics = regression_metrics(y_test, predict_nps(baseline, X_test))

    # Comparação justa com a abordagem de classificação: o melhor classificador da
    # validação cruzada é avaliado no mesmo teste, pela mesma métrica de ordenação.
    best_classifier_name = classification_cv.loc[0, "modelo"]
    classifier = make_pipeline(classification_candidates()[best_classifier_name]).fit(
        X_train, (y_train < config.DETRACTOR_LIMIT).astype(int)
    )
    classifier_auc = roc_auc_score(
        (y_test < config.DETRACTOR_LIMIT).astype(int),
        classifier.predict_proba(X_test)[:, 1],
    )

    # Modelo final: mesmo algoritmo, re-treinado com toda a base para uso em produção.
    # As métricas reportadas continuam sendo as do teste, que o modelo avaliado não viu.
    X_all, y_all = get_features_and_target(df)
    final_model = make_pipeline(regression_candidates()[best_regressor_name]).fit(
        X_all, y_all
    )
    impacts = unit_impacts(final_model)

    results = {
        "data_treino": date.today().isoformat(),
        "modelo_escolhido": best_regressor_name,
        "variaveis_de_entrada": config.MODEL_FEATURES,
        "variaveis_excluidas_por_vazamento": config.LEAKAGE_COLUMNS,
        "linhas_treino": len(train_df),
        "linhas_teste": len(test_df),
        "validacao_cruzada_regressao": regression_cv.round(3).to_dict(orient="records"),
        "validacao_cruzada_classificacao": classification_cv.round(3).to_dict(
            orient="records"
        ),
        "teste_modelo_escolhido": regression_metrics(y_test, y_pred),
        "teste_baseline_media": baseline_metrics,
        "teste_ordenacao_detratores": detractor_ranking_metrics(y_test, y_pred),
        "teste_melhor_classificador": {
            "modelo": best_classifier_name,
            "ROC_AUC": round(float(classifier_auc), 3),
        },
        "faixas_de_risco_teste": risk_tier_table(y_test, y_pred)
        .reset_index()
        .to_dict(orient="records"),
        "impacto_por_unidade": None if impacts is None else impacts.round(3).to_dict(),
    }

    if save:
        config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(final_model, config.MODEL_PATH)
        with open(config.METRICS_PATH, "w", encoding="utf-8") as metrics_file:
            json.dump(results, metrics_file, ensure_ascii=False, indent=2)

    # Objetos extras para quem chama a função (ex.: notebook); não vão para o JSON
    results["_objetos"] = {
        "train_df": train_df,
        "test_df": test_df,
        "model_avaliado": model,
        "modelo_final": final_model,
        "classificador": classifier,
        "y_test": y_test,
        "y_pred": y_pred,
    }
    return results


def main() -> None:
    """Treina, avalia e salva o modelo e as métricas."""
    config.use_utf8_output()
    results = run_training(save=True)

    pd.set_option("display.width", 160)
    print("Validação cruzada (treino) - regressão")
    print(pd.DataFrame(results["validacao_cruzada_regressao"]).to_string(index=False))
    print("\nValidação cruzada (treino) - classificação de detratores")
    print(
        pd.DataFrame(results["validacao_cruzada_classificacao"]).to_string(index=False)
    )
    print(f"\nModelo escolhido: {results['modelo_escolhido']}")
    print(f"Teste - modelo escolhido: {results['teste_modelo_escolhido']}")
    print(f"Teste - baseline (média): {results['teste_baseline_media']}")
    print(
        f"Teste - ordenação de detratores pela nota prevista: {results['teste_ordenacao_detratores']}"
    )
    print(f"Teste - melhor classificador: {results['teste_melhor_classificador']}")
    print("\nFaixas de risco no teste")
    print(pd.DataFrame(results["faixas_de_risco_teste"]).to_string(index=False))
    print(f"\nModelo salvo em: {config.MODEL_PATH.relative_to(config.PROJECT_ROOT)}")
    print(f"Métricas salvas em: {config.METRICS_PATH.relative_to(config.PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
