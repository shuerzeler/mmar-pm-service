import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer

log = pm4py.read_xes("evaluation/data/running-example.xes")
df = pm4py.convert_to_dataframe(log)
print(f"Cases: {df['case:concept:name'].nunique()}")
print(f"Events: {len(df)}")

log = xes_importer.apply("evaluation/data/pdc2024_000000.xes")
print(f"Cases: {len(log)}")
print(f"Events: {sum(len(trace) for trace in log)}")

log = xes_importer.apply("evaluation/data/Road_Traffic_Fine_Management_Process.xes")
print(f"Cases: {len(log)}")
print(f"Events: {sum(len(trace) for trace in log)}")

import pandas as pd
df = pd.read_csv("evaluation/data/P2P.csv")
print(f"Cases: {df['Order_ID'].nunique()}")
print(f"Events: {len(df)}")