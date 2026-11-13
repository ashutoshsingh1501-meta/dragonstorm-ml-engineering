"""Read-only ONNX nested resize and pixel normalization audit (D4-02/04).

Run from anywhere with the isolated inspection venv on the VM.
"""
from pathlib import Path
import onnx
from onnx import numpy_helper

path = Path.home() / "dragonstorm-lab/model_repository/ssd_mobilenet_v1_12/1/model.onnx"
model = onnx.load(str(path), load_external_data=False)
graph = model.graph
constants = {x.name: numpy_helper.to_array(x) for x in graph.initializer}
print("Producer:", model.producer_name, model.producer_version)
print("IR:", model.ir_version, "Opsets:", [(o.domain, o.version) for o in model.opset_import])
for direction, tensors in (("input", graph.input), ("output", graph.output)):
    for tensor in tensors:
        t = tensor.type.tensor_type
        dims = [d.dim_value if d.HasField("dim_value") else d.dim_param or "?" for d in t.shape.dim]
        print(direction, tensor.name, onnx.TensorProto.DataType.Name(t.elem_type), dims)
for index, node in enumerate(graph.node):
    if node.name in ("Preprocessor/mul", "Preprocessor/sub"):
        print(index, node.name, node.op_type, list(node.input))
for name in ("Preprocessor/mul/x:0", "const_fold_opt__6209", "Preprocessor/map/while/ResizeImage/stack:0"):
    print("initializer", name, constants.get(name, "(not top-level initializer)"))
def walk(g, prefix="MAIN"):
    for i, node in enumerate(g.node):
        if node.op_type == "Resize":
            print("Resize location:", prefix, i, node.name, "inputs:", list(node.input))
            for a in node.attribute:
                print(" attribute", a.name, onnx.helper.get_attribute_value(a))
        for attr in node.attribute:
            if attr.type == onnx.AttributeProto.GRAPH:
                walk(attr.g, f"{prefix}/{node.op_type}[{i}]")
            elif attr.type == onnx.AttributeProto.GRAPHS:
                for j, sg in enumerate(attr.graphs):
                    walk(sg, f"{prefix}/{node.op_type}[{i}]/{j}")
walk(graph)
print("ONNX PREPROCESSING INSPECTION COMPLETE")
