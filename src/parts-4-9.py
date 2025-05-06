import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms import bipartite
import community as community_louvain
import pandas as pd
import json

# ---------------------------
# DATASET
# ---------------------------

df = pd.read_csv("edges.csv")
print(df.head())

reports = df['source'].unique()
agencies = df['target'].unique()

with open("organisations_with_types.json", "r", encoding="utf-8") as f:
    roles_data = json.load(f)

# ---------------------------
# Part 4: Bipartite Graph Creation
# ---------------------------

# Create bipartite graph
B = nx.Graph()

# Add edges from DataFrame
B.add_nodes_from(reports, bipartite=0)   # Set 0: Reports
B.add_nodes_from(agencies, bipartite=1)  # Set 1: Agencies
edges = list(df.itertuples(index=False, name=None))
B.add_edges_from(edges)

# Visualize bipartite graph
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(B, seed=42)
colors = ['skyblue' if node in reports else 'lightgreen' for node in B.nodes()]
nx.draw(B, pos, with_labels=True, node_color=colors)
plt.title("Bipartite Graph: Reports ↔ Agencies")
plt.show()

# ---------------------------
# Part 5: Projected Agency Graph
# ---------------------------

# Project to agency-only graph
agency_proj = bipartite.weighted_projected_graph(B, agencies)

# Visualize weighted agency graph
plt.figure(figsize=(10, 6))
edge_weights = [agency_proj[u][v]['weight'] for u, v in agency_proj.edges()]
nx.draw(agency_proj, with_labels=True, width=edge_weights, node_color="lightcoral")
plt.title("Agency-Only Projected Graph")
plt.show()



# ---------------------------
# Assortativity
# ---------------------------

# Build role map
role_map = {v["shortname"]: v["type"]["name"] for v in roles_data.values()}
# Assigns roles to nnodes
nx.set_node_attributes(agency_proj, role_map, "role")
# Check for missing roles
missing_roles = [n for n in agency_proj.nodes() if "role" not in agency_proj.nodes[n]]
if missing_roles:
    print("Warning: These agencies have no assigned role:", missing_roles)
# ---------------------------
# Part 7: Centrality Measures
# ---------------------------
degree_centrality = nx.degree_centrality(agency_proj)
betweenness_centrality = nx.betweenness_centrality(agency_proj)
closeness_centrality = nx.closeness_centrality(agency_proj)
eigenvector_centrality = nx.eigenvector_centrality(agency_proj)

# Display top agencies by centrality
print("\n--- Centrality Measures ---")
print("Top Degree Centrality:", sorted(degree_centrality.items(), key=lambda x: -x[1])[:3])
print("Top Betweenness Centrality:", sorted(betweenness_centrality.items(), key=lambda x: -x[1])[:3])
print("Top Closeness Centrality:", sorted(closeness_centrality.items(), key=lambda x: -x[1])[:3])
print("Top Eigenvector Centrality:", sorted(eigenvector_centrality.items(), key=lambda x: -x[1])[:3])

# ---------------------------
# Part 8: Role Assortativity
# ---------------------------
assortativity = nx.attribute_assortativity_coefficient(agency_proj, 'role')
print(f"\nRole Assortativity Coefficient: {assortativity:.3f}")

# ---------------------------
# Part 9: Community Detection (Louvain)
# ---------------------------
partition = community_louvain.best_partition(agency_proj)
modularity_score = nx.algorithms.community.modularity(agency_proj, [
    [node for node in partition if partition[node] == com]
    for com in set(partition.values())
])

# Add community info as node attribute
nx.set_node_attributes(agency_proj, partition, "community")

print(f"\nLouvain Modularity Score: {modularity_score:.3f}")
print("Communities:", {node: f"Group {group}" for node, group in partition.items()})

# Visualize with communities
plt.figure(figsize=(10, 6))
colors = [partition[n] for n in agency_proj.nodes()]
nx.draw(agency_proj, with_labels=True, node_color=colors, cmap=plt.cm.Set3)
plt.title("Louvain Community Detection (Agency Graph)")
plt.show()
