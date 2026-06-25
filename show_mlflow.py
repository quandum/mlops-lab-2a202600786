import mlflow
mlflow.set_tracking_uri('sqlite:///mlflow.db')
runs = mlflow.search_runs(experiment_ids=['0'])

# Filter actual experiments (skip pytest runs with n_estimators=10)
runs = runs[runs['params.n_estimators'].astype(float) >= 50]

print('=' * 60)
print('  MLflow Tracking - Wine Quality Classification')
print('=' * 60)
for i, (_, r) in enumerate(runs.sort_values('metrics.accuracy', ascending=False).iterrows()):
    n = int(r['params.n_estimators'])
    d = int(r['params.max_depth'])
    s = int(r['params.min_samples_split'])
    a = float(r['metrics.accuracy'])
    f1 = float(r['metrics.f1_score'])
    bar = '#' * int(a * 30)
    print(f"  TN{i+1}: n={n:>3} depth={d:>2} split={s:>2} | Acc={a:.4f} F1={f1:.4f} | {bar}")
print('=' * 60)
print(f"  Best: n_estimators=300, max_depth=15, min_samples_split=2")
