Following refactors should be done for the `train` page UI and api

# UI modifications
- below the `Name` field create a new field named 'Training Data' that'll expose a file selection input.
Acceptable file types are csv, xls and xlsx. The selected file should be sent to BE with the rest of 
of the form on form submission.

- for xbg model following hyperparams should be exposed grouped under specific sub sections in the input form. From the recommendation columns below pick a value as a default input for that hyperparam. Modify
the required places so that on form submission a plain dictionary (don't need to consider any grouping while making the dictionary) of hyperparams are sent to backend.

* Booster & Tree Structure Parameters

| Parameter                   | Recommendation                                        |
| --------------------------- | ----------------------------------------------------- |
| **booster**                 | `['gbtree', 'dart']` (avoid gblinear unless required) |
| **tree_method**             | `['auto', 'exact', 'approx', 'hist', 'gpu_hist']`     |
| **grow_policy**             | `['depthwise', 'lossguide']`                          |
| **max_depth**               | `3–10`                                                |
| **max_leaves**              | `16–256` (lossguide only)                             |
| **max_bin**                 | `64–512`                                              |
| **min_child_weight**        | `1–10`                                                |
| **gamma**                   | `0–10`                                                |
| **max_delta_step**          | `0–10`                                                |
| **monotone_constraints**    | e.g. `{'0':1,'2':-1}`                                 |
| **interaction_constraints** | e.g. `[['f1','f3']]`                                  |


* Learning / Optimization Parameters

| Parameter                 | Recommendation                  |
| ------------------------- | ------------------------------- |
| **learning_rate**         | `0.01–0.3`                      |
| **n_estimators**          | `100–2000`                      |
| **early_stopping_rounds** | `10–100`                        |
| **sampling_method**       | `['uniform', 'gradient_based']` |


* Sampling Parameters

| Parameter             | Recommendation |
| --------------------- | -------------- |
| **subsample**         | `0.5–1.0`      |
| **colsample_bytree**  | `0.3–1.0`      |
| **colsample_bylevel** | `0.3–1.0`      |
| **colsample_bynode**  | `0.3–1.0`      |

* Regularization Parameters

| Parameter           | Recommendation |
| ------------------- | -------------- |
| **reg_alpha (L1)**  | `0–10`         |
| **reg_lambda (L2)** | `0.1–10`       |

* Randomness & Determinism

| Parameter         | Recommendation |
| ----------------- | -------------- |
| **random_state**  | integer        |
| **seed**          | integer        |
| **deterministic** | `True/False`   |



- for lgb model following hyperparams should be exposed grouped under specific sub sections in the input form. From the recommendation column pick a value as a default input for that hyperparam. Modify
the required places so that on form submission a plain dictionary (don't need to consider any grouping while making the dictionary) of hyperparams are sent to backend.
   
* Core Booster / Tree Structure Parameters

| Parameter                   | Recommended Range / Values |
| --------------------------- | -------------------------- |
| **boosting_type**           | `['gbdt', 'dart', 'goss']` |
| **num_leaves**              | `31–1023` (common: 31–255) |
| **max_depth**               | `-1` (no limit) or `3–12`  |
| **min_data_in_leaf**        | `10–100`                   |
| **min_sum_hessian_in_leaf** | `0.001–10`                 |
| **max_bin**                 | `63–511`                   |
| **extra_trees**             | `True/False`               |
| **extra_seed**              | integer                    |
| **min_split_gain**          | `0–10`                     |
| **path_smooth**             | `0–1`                      |

* Learning / Optimization Parameters

| Parameter                          | Recommended Range / Values       |
| ---------------------------------- | -------------------------------- |
| **learning_rate**                  | `0.005–0.3` (common: 0.01–0.1)   |
| **num_iterations**                 | `100–5000`                       |
| **early_stopping_rounds**          | `10–200`                         |
| **bagging_freq**                   | `0–10`                           |
| **bagging_seed**                   | integer                          |
| **feature_fraction_seed**          | integer                          |
| **dart** (if boosting_type='dart') | includes drop parameters (below) |

* Sampling Parameters

| Parameter                    | Recommended Range / Values         |
| ---------------------------- | ---------------------------------- |
| **bagging_fraction**         | `0.5–1.0`                          |
| **feature_fraction**         | `0.3–1.0`                          |
| **feature_fraction_bynode**  | `0.3–1.0`                          |
| **feature_fraction_bylevel** | `0.3–1.0`                          |
| **poisson**                  | `True/False` (Poisson subsampling) |

* Regularization Parameters

| Parameter             | Recommended Range / Values       |
| --------------------- | -------------------------------- |
| **lambda_l1**         | `0–10`                           |
| **lambda_l2**         | `0–10`                           |
| **min_gain_to_split** | `0–10` (alias of min_split_gain) |

* DART-Specific Parameters

| Parameter             | Recommended Range / Values |
| --------------------- | -------------------------- |
| **drop_rate**         | `0.1–0.5`                  |
| **skip_drop**         | `0–0.5`                    |
| **max_drop**          | `10–100`                   |
| **uniform_drop**      | `True/False`               |
| **xgboost_dart_mode** | `True/False`               |
| **drop_seed**         | integer                    |

* GOSS-Specific Parameters

| Parameter      | Recommended Range / Values |
| -------------- | -------------------------- |
| **top_rate**   | `0.1–0.5`                  |
| **other_rate** | `0.1–0.5`                  |

* Randomness & Determinism

| Parameter         | Recommended Range / Values |
| ----------------- | -------------------------- |
| **seed**          | integer                    |
| **deterministic** | `True/False`               |


# Backend modifications
The POST api `/api/train` should be modified accordingly to accomodate above concerns. Following should be maintained
- current input of api model, custom_name, training_data_start_date, training_data_end_date should remain
as is.
- a multipart file should be accepted to propagate the user's selected file
- a plain dictionary should be accepted to propagate the model-sepecific hyperparams
- a new function named `train_model_with_hyperparams` should be implemented in model_service.py that'll
be used to trained the model using these inputs following the implementation of existing `train_model`
method. Following should be maintained with care using existing convention 
    - proper defintion of PredictionJobDataClass using the model and hyperparam
    - training start and end date
    - pj saving
    - model saving
- the api response should be modified accordingly
- there's no use of the file, it can be ignored. 

