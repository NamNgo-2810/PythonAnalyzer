import ast
import gc

import objgraph
import graphviz
import matplotlib.pyplot as plt
import sys
import os
from io import BytesIO


def load_code(file_path):
    """
    Load code from a Python file.
    """
    with open(file_path, 'r') as file:
        return file.read()


def save_cfg_image(cfg, output_file="cfg"):
    """
    Saves the control-flow graph as an image file.
    """
    cfg.format = 'png'
    cfg.render(filename=output_file, cleanup=True)
    print(f"Control-Flow Graph saved as {output_file}")


def generate_cfg(code):
    """
    Parses Python code to generate a detailed control-flow graph and returns a graphviz graph.
    """
    tree = ast.parse(code)
    dot = graphviz.Digraph(comment='Control Flow Graph')

    # Helper function to add nodes with more detailed information
    def add_cfg_node(node, label):
        node_id = str(id(node))
        dot.node(node_id, label)
        return node_id

    # Recursively add nodes and edges for more detailed control flow
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_node = add_cfg_node(node, f"Function: {node.name}")
            for stmt in node.body:
                stmt_node = add_cfg_node(stmt, f"Statement: {ast.dump(stmt)}")
                dot.edge(func_node, stmt_node)
        elif isinstance(node, ast.If):
            if_node = add_cfg_node(node, f"If Condition: {ast.dump(node.test)}")
            for stmt in node.body:
                stmt_node = add_cfg_node(stmt, f"Statement: {ast.dump(stmt)}")
                dot.edge(if_node, stmt_node)
            for stmt in node.orelse:
                stmt_node = add_cfg_node(stmt, f"Else Statement: {ast.dump(stmt)}")
                dot.edge(if_node, stmt_node)
        elif isinstance(node, ast.While):
            while_node = add_cfg_node(node, f"While Loop: {ast.dump(node.test)}")
            for stmt in node.body:
                stmt_node = add_cfg_node(stmt, f"Statement: {ast.dump(stmt)}")
                dot.edge(while_node, stmt_node)
        elif isinstance(node, ast.For):
            for_node = add_cfg_node(node, f"For Loop: {ast.dump(node.target)}")
            for stmt in node.body:
                stmt_node = add_cfg_node(stmt, f"Statement: {ast.dump(stmt)}")
                dot.edge(for_node, stmt_node)

    return dot

def visualize_memory_allocation(output_file="memory_allocation.png"):
    """
    Uses objgraph to display detailed memory allocation/deallocation of specific types.
    """
    gc.collect()  # Clear unreferenced objects to show current memory state

    # Visualize memory growth with objgraph and save detailed memory reference graph
    fig, ax = plt.subplots()
    objgraph.show_most_common_types(limit=10)
    objgraph.show_growth(limit=10)
    ax.text(0.5, 0.5, "Memory allocation for most common object types:", ha='center', wrap=True)
    ax.axis("off")

    # Save backrefs for a sample object to capture memory relationships
    objgraph.show_backrefs([objgraph.by_type('dict')[0]], filename=output_file)
    print(f"Memory Allocation image saved as {output_file}")


def illustrate_pointers(code, output_file="pointers.png"):
    """
    Illustrates pointer-like reference usage by tracking object IDs, reference counts, and variable mapping.
    """
    exec_env = {}
    exec(code, exec_env)  # Execute code in a controlled environment

    fig, ax = plt.subplots()

    # Collect pointer information for each variable in the execution environment
    pointer_info = [
        f"{var}: ID {id(val)}, Ref Count {sys.getrefcount(val)}"
        for var, val in exec_env.items() if not var.startswith("__")
    ]

    # Display pointer information in the plot
    pointer_text = "\n".join(pointer_info)
    ax.text(0.5, 0.5, pointer_text, fontsize=12, ha='center', wrap=True)
    ax.axis("off")

    # Save the image and close the figure
    plt.savefig(output_file, bbox_inches='tight')
    plt.close(fig)
    print(f"Pointer Usage image saved as {output_file}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_code.py <python_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    if not os.path.isfile(input_file):
        print(f"File not found: {input_file}")
        sys.exit(1)

    code = load_code(input_file)

    # Generate and save CFG
    cfg = generate_cfg(code)
    save_cfg_image(cfg, output_file="cfg")

    # Generate and save memory allocation
    visualize_memory_allocation(output_file="memory_allocation.png")

    # Generate and save pointer usage
    illustrate_pointers(code, output_file="pointers.png")


if __name__ == "__main__":
    main()
