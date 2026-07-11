from helpers.uuid_resolver import getBPMNUUID
from helpers.signin import login
from pm4py.objects.bpmn.obj import BPMN
from datetime import datetime
import uuid
import requests
import networkx as nx

#Exporter that creates the payload and makes call to mmar_server to bridge PM4Py BPMN to mmar datamodel

BASE_URL = "http://mmar-server:8000"

def createBPMN(bpmn):
    #get token for API calls
    token = login()

    #get uuids needed to create BPMN, its classes and relation
    bpmn_uuids = getBPMNUUID(token)

    #calculate coordinates for BPMN
    layout = compute_bpmn_layout(bpmn)
    
    #create random uuid for new scene instance
    instance_uuid = str(uuid.uuid4())

    #create dict for node uuid mapping (needed to create sequence flows)
    node_uuid_map = {}

    #create object to save class instances
    class_instances = []

    #for each node in BPMN object first create uuid, then create and add node to class instance object
    for i, node in enumerate(bpmn.get_nodes()):
        node_instance_uuid = str(uuid.uuid4())
        node_uuid_map[node.get_id()] = node_instance_uuid
        coords = layout.get(node.get_id(), {"x": 0, "y": 0, "z": 0})
        label = node.get_name() if node.get_name() else f"node_{i}"

        #set correct class for BPMN node type
        if isinstance(node, BPMN.StartEvent):
            class_uuid = bpmn_uuids["start_event"]
        elif isinstance(node, BPMN.EndEvent):
            class_uuid = bpmn_uuids["end_event"]
        elif isinstance(node, BPMN.Task):
            class_uuid = bpmn_uuids["task"]
        elif isinstance(node, BPMN.ExclusiveGateway):
            class_uuid = bpmn_uuids["exclusive_gateway"]
        elif isinstance(node, BPMN.ParallelGateway):
            class_uuid = bpmn_uuids["parallel_gateway"]
        else:
            #in case of unknown node type, set task
            class_uuid = bpmn_uuids["task"]

        class_instances.append({
            "uuid": node_instance_uuid,
            "uuid_class": class_uuid,
            "name": label,
            "attribute_instance": [
                {
                    "uuid": str(uuid.uuid4()),
                    "uuid_attribute": bpmn_uuids["task_name_attr"],
                    "name": "Name",
                    "value": label
                }
            ],
            "coordinates_2d": coords
        })

    #create sequence flows to connect nodes of BPMN
    relationclasses_instances = []
    for flow in bpmn.get_flows():
        source_id = flow.get_source().get_id()
        target_id = flow.get_target().get_id()

        source_instance_uuid = node_uuid_map.get(source_id)
        target_instance_uuid = node_uuid_map.get(target_id)

        #skip if source or target node is not found
        if not source_instance_uuid or not target_instance_uuid:
            continue

        #set source and target
        source_data = next(ci for ci in class_instances if ci["uuid"] == source_instance_uuid)
        target_data = next(ci for ci in class_instances if ci["uuid"] == target_instance_uuid)

        #generate random uuids for flow objects
        flow_instance_uuid = str(uuid.uuid4())
        role_from_instance_uuid = str(uuid.uuid4())
        role_to_instance_uuid = str(uuid.uuid4())

        relationclasses_instances.append({
            "uuid": flow_instance_uuid,
            "uuid_relationclass": bpmn_uuids["sequence_flow"],
            "uuid_class": bpmn_uuids["sequence_flow"],
            "name": "Sequence Flow",
            "attribute_instance": [],
            "role_instance_from": {
                "uuid": role_from_instance_uuid,
                "uuid_role": bpmn_uuids["sequence_flow_role_from"],
                "uuid_has_reference_class_instance": source_instance_uuid
            },
            "role_instance_to": {
                "uuid": role_to_instance_uuid,
                "uuid_role": bpmn_uuids["sequence_flow_role_to"],
                "uuid_has_reference_class_instance": target_instance_uuid
            },
            "uuid_role_instance_from": role_from_instance_uuid,
            "uuid_role_instance_to": role_to_instance_uuid,
            "line_points": [
                {"UUID": source_instance_uuid, "Point": source_data["coordinates_2d"]},
                {"UUID": target_instance_uuid, "Point": target_data["coordinates_2d"]}
            ]
        })

    #create payload
    payload = {
        "uuid": instance_uuid,
        "uuid_scene_type": bpmn_uuids["metamodel"],
        "name": f"PM_BPMN_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "class_instances": class_instances,
        "relationclasses_instances": relationclasses_instances
    }

    #make call to save BPMN
    response = requests.post(
        f"{BASE_URL}/instances/sceneInstances/{instance_uuid}",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )

    return response.json()

#function to compute coordinates of bpmn components with Graphviz
def compute_bpmn_layout(bpmn, x_scale=0.003, y_scale=0.015):
    #use NetworkX library to build directed graph
    G = nx.DiGraph()
    
    #add BPMN nodes and flows as graph nodes and edges; node ids are unique
    for node in bpmn.get_nodes():
        G.add_node(node.get_id())
    for flow in bpmn.get_flows():
        G.add_edge(flow.get_source().get_id(), flow.get_target().get_id())
    
    #find start and end nodes by type to pin them to left and right side of the layout
    start_node = next((n for n in bpmn.get_nodes() if isinstance(n, BPMN.StartEvent)), None)
    end_node = next((n for n in bpmn.get_nodes() if isinstance(n, BPMN.EndEvent)), None)
    
    #create graph to be used by Graphviz
    A = nx.nx_agraph.to_agraph(G)
    A.graph_attr["rankdir"] = "LR"
    A.graph_attr["ranksep"] = "1.5"
    A.graph_attr["nodesep"] = "0.8"
    
    #pin start and end nodes if found; if needed since BPMN may lack start and end
    if start_node:
        A.add_subgraph([start_node.get_id()], rank="min")
    if end_node:
        A.add_subgraph([end_node.get_id()], rank="max")
    
    #calculate layout with Graphviz
    A.layout(prog="dot")
    
    #get coordinates
    pos = {}
    for node in A.nodes():
        x, y = node.attr["pos"].split(",")
        pos[str(node)] = (float(x), float(y))
    
    #center coordinates around origin for mmar canvas
    mid_x = (min(x for x, y in pos.values()) + max(x for x, y in pos.values())) / 2
    mid_y = (min(y for x, y in pos.values()) + max(y for x, y in pos.values())) / 2
    
    #scale and return position directly
    return {name: {"x": float(x - mid_x) * x_scale, "y": float(y - mid_y) * y_scale, "z": 0}
            for name, (x, y) in pos.items()}