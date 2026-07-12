from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.conversion.log import converter as log_converter
from pm4py import discover_petri_net_alpha, discover_petri_net_inductive, discover_petri_net_heuristics, discover_bpmn_inductive
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.visualization.bpmn import visualizer as bpmn_visualizer
import pm4py
import pandas as pd
import requests
import time
import csv
import os

#Base URL and data paths
PM_SERVICE_URL = "http://localhost:8001"
DATA_DIR = "evaluation/data/"
RESULTS_DIR = "evaluation/results/"
#create results folder if not existing
os.makedirs(RESULTS_DIR, exist_ok=True)

#implemented algorithms that should be called
ALGORITHMS = ["alpha", "inductive", "heuristic", "bpmn_inductive"]

#datasets
DATASETS = [
    {
        "name": "Running Example",
        "path": f"{DATA_DIR}running-example.xes",
        "type": "xes"
    },
    {
        "name": "PDC 2024",
        "path": f"{DATA_DIR}pdc2024_000000.xes",
        "type": "xes"
    },
    {
        "name": "Road Traffic Fine Management",
        "path": f"{DATA_DIR}Road_Traffic_Fine_Management_Process.xes",
        "type": "xes"
    },
    {
        "name": "P2P",
        "path": f"{DATA_DIR}P2P.csv",
        "type": "csv",
        "case_id": "Order_ID",
        "activity_name": "Activity",
        "timestamp": "Timestamp"
    }
]

#----------------------------------------PM4Py calls--------------------------------------------------

#parse logs do directly run in PM4Py
def load_event_log(dataset):
    if dataset["type"] == "xes":
        return xes_importer.apply(dataset["path"])
    elif dataset["type"] == "csv":
        df = pd.read_csv(dataset["path"])
        df = pm4py.format_dataframe(
            df,
            case_id=dataset["case_id"],
            activity_key=dataset["activity_name"],
            timestamp_key=dataset["timestamp"]
        )
        return log_converter.apply(df)

#execute algorithms using PM4Py directly
def run_pm4py_directly(event_log, algorithm, dataset_name):
    if algorithm == "alpha":
        net, im, fm = discover_petri_net_alpha(event_log)
        gviz = pn_visualizer.apply(net, im, fm)
        pn_visualizer.save(gviz, f"{RESULTS_DIR}{dataset_name}_{algorithm}.png")
        return {"places": len(net.places), "transitions": len(net.transitions), "arcs": len(net.arcs)}
    elif algorithm == "inductive":
        net, im, fm = discover_petri_net_inductive(event_log)
        gviz = pn_visualizer.apply(net, im, fm)
        pn_visualizer.save(gviz, f"{RESULTS_DIR}{dataset_name}_{algorithm}.png")
        return {"places": len(net.places), "transitions": len(net.transitions), "arcs": len(net.arcs)}
    elif algorithm == "heuristic":
        net, im, fm = discover_petri_net_heuristics(event_log)
        gviz = pn_visualizer.apply(net, im, fm)
        pn_visualizer.save(gviz, f"{RESULTS_DIR}{dataset_name}_{algorithm}.png")
        return {"places": len(net.places), "transitions": len(net.transitions), "arcs": len(net.arcs)}
    elif algorithm == "bpmn_inductive":
        bpmn = discover_bpmn_inductive(event_log)
        gviz = bpmn_visualizer.apply(bpmn)
        bpmn_visualizer.save(gviz, f"{RESULTS_DIR}{dataset_name}_{algorithm}.png")
        return {"nodes": len(list(bpmn.get_nodes())), "flows": len(list(bpmn.get_flows()))}

#on all datasets execute the all algorithms directly via PM4Py
pm4py_results = {}
for dataset in DATASETS:
    print(f"Loading {dataset['name']}...")
    pm4py_results[dataset["name"]] = {}
    for algorithm in ALGORITHMS:
        print(f"  Running {algorithm} via PM4Py...")
        
        # time the full PM4Py pipeline with loading
        t_start = time.time()
        event_log = load_event_log(dataset)
        result = run_pm4py_directly(event_log, algorithm, dataset["name"].replace(" ", "_"))
        result["pm4py_time"] = round(time.time() - t_start, 3)
        
        pm4py_results[dataset["name"]][algorithm] = result
        print(f"    Done in {result['pm4py_time']}s")

#----------------------------------------MM-AR calls--------------------------------------------------

#call route for datasets and count elements in mmar response
def call_pm_service(dataset, algorithm):
    t_start = time.time()
    
    if dataset["type"] == "xes":
        with open(dataset["path"], "rb") as f:
            files = {"file": (dataset["path"], f, "application/octet-stream")}
            response = requests.post(
                f"{PM_SERVICE_URL}/run?algorithm={algorithm}",
                files=files
            )
    elif dataset["type"] == "csv":
        with open(dataset["path"], "rb") as f:
            files = {"file": (dataset["path"], f, "text/csv")}
            data = {
                "case_id": dataset["case_id"],
                "activity_name": dataset["activity_name"],
                "timestamp": dataset["timestamp"]
            }
            response = requests.post(
                f"{PM_SERVICE_URL}/run?algorithm={algorithm}",
                files=files,
                data=data
            )
    
    total_time = round(time.time() - t_start, 3)
    
    if response.status_code != 200:
        print(f"    ERROR: {response.status_code} {response.text}")
        return None
    
    scene = response.json()
    
    # count elements from mmar response
    if algorithm == "bpmn_inductive":
        return {
            "nodes": len(scene.get("class_instances", [])),
            "flows": len(scene.get("relationclasses_instances", [])),
            "total_time": total_time
        }
    else:
        return {
            "places": len([ci for ci in scene.get("class_instances", []) if ci.get("name") == "Place"]),
            "transitions": len([ci for ci in scene.get("class_instances", []) if ci.get("name") == "Transition"]),
            "arcs": len(scene.get("relationclasses_instances", [])),
            "total_time": total_time
        }

#on all datasets call the pm service for all algorithms
mmar_results = {}
for dataset in DATASETS:
    print(f"\nCalling PM service for {dataset['name']}...")
    mmar_results[dataset["name"]] = {}
    for algorithm in ALGORITHMS:
        print(f"  Calling {algorithm} via PM service...")
        mmar_results[dataset["name"]][algorithm] = call_pm_service(dataset, algorithm)
        if mmar_results[dataset["name"]][algorithm]:
            print(f"    Done in {mmar_results[dataset['name']][algorithm]['total_time']}s")

#----------------------------------------Comparison--------------------------------------------------

#comparison and output
rows = []
for dataset in DATASETS:
    name = dataset["name"]
    for algorithm in ALGORITHMS:
        pm4py_r = pm4py_results[name][algorithm]
        mmar_r = mmar_results[name].get(algorithm)

        #if mm-ar has no results
        if mmar_r is None:
            row = {
                "dataset": name,
                "algorithm": algorithm,
                "pm4py_places": None,
                "mmar_places": None,
                "pm4py_transitions": None,
                "mmar_transitions": None,
                "pm4py_arcs": None,
                "mmar_arcs": None,
                "pm4py_nodes": None,
                "mmar_nodes": None,
                "pm4py_flows": None,
                "mmar_flows": None,
                "pm4py_time_s": pm4py_r.get("pm4py_time"),
                "total_time_s": None,
                "mmar_overhead_s": None,
                "match": "ERROR"
            }
        else:
            mmar_overhead = round(mmar_r["total_time"] - pm4py_r["pm4py_time"], 3)

            #bpmn checks nodes and flows
            if algorithm == "bpmn_inductive":
                match = pm4py_r["nodes"] == mmar_r["nodes"] and pm4py_r["flows"] == mmar_r["flows"]
                row = {
                    "dataset": name,
                    "algorithm": algorithm,
                    "pm4py_nodes": pm4py_r["nodes"],
                    "mmar_nodes": mmar_r["nodes"],
                    "pm4py_flows": pm4py_r["flows"],
                    "mmar_flows": mmar_r["flows"],
                    "pm4py_places": None,
                    "mmar_places": None,
                    "pm4py_transitions": None,
                    "mmar_transitions": None,
                    "pm4py_arcs": None,
                    "mmar_arcs": None,
                    "pm4py_time_s": pm4py_r["pm4py_time"],
                    "total_time_s": mmar_r["total_time"],
                    "mmar_overhead_s": mmar_overhead,
                    "match": "✓" if match else "✗"
                }
            #petri nets are checked for places, transitions and arcs
            else:
                match = (pm4py_r["places"] == mmar_r["places"] and
                         pm4py_r["transitions"] == mmar_r["transitions"] and
                         pm4py_r["arcs"] == mmar_r["arcs"])
                row = {
                    "dataset": name,
                    "algorithm": algorithm,
                    "pm4py_places": pm4py_r["places"],
                    "mmar_places": mmar_r["places"],
                    "pm4py_transitions": pm4py_r["transitions"],
                    "mmar_transitions": mmar_r["transitions"],
                    "pm4py_arcs": pm4py_r["arcs"],
                    "mmar_arcs": mmar_r["arcs"],
                    "pm4py_nodes": None,
                    "mmar_nodes": None,
                    "pm4py_flows": None,
                    "mmar_flows": None,
                    "pm4py_time_s": pm4py_r["pm4py_time"],
                    "total_time_s": mmar_r["total_time"],
                    "mmar_overhead_s": mmar_overhead,
                    "match": "✓" if match else "✗"
                }
        rows.append(row)

# print to console
print("\n" + "="*80)
print("STRUCTURAL CORRECTNESS AND PERFORMANCE RESULTS")
print("="*80)
for row in rows:
    print(f"\n{row['dataset']} — {row['algorithm']}")
    if row["algorithm"] == "bpmn_inductive":
        print(f"  Nodes:  PM4Py={row['pm4py_nodes']} MMAR={row['mmar_nodes']}")
        print(f"  Flows:  PM4Py={row['pm4py_flows']} MMAR={row['mmar_flows']}")
    else:
        print(f"  Places:      PM4Py={row['pm4py_places']} MMAR={row['mmar_places']}")
        print(f"  Transitions: PM4Py={row['pm4py_transitions']} MMAR={row['mmar_transitions']}")
        print(f"  Arcs:        PM4Py={row['pm4py_arcs']} MMAR={row['mmar_arcs']}")
    print(f"  Match:       {row['match']}")
    print(f"  PM4Py time:  {row['pm4py_time_s']}s")
    print(f"  Total time:  {row['total_time_s']}s")
    print(f"  MMAR overhead: {row['mmar_overhead_s']}s")

# write to CSV
csv_path = f"{RESULTS_DIR}results.csv"
fieldnames = ["dataset", "algorithm", "pm4py_places", "mmar_places", 
              "pm4py_transitions", "mmar_transitions", "pm4py_arcs", "mmar_arcs",
              "pm4py_nodes", "mmar_nodes", "pm4py_flows", "mmar_flows",
              "pm4py_time_s", "total_time_s", "mmar_overhead_s", "match"]

with open(csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"\nResults saved to {csv_path}")