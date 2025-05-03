import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms import bipartite
import community as community_louvain

import random

# ---------------------------
# Part 4: Bipartite Graph Creation
# ---------------------------

# Simulated data:
### TODO CHANGE WHEN KNOW THE REAL DATA!!!
report_agency_data = {
    "Report1": ["WHO", "UNICEF", "BBC"],
    "Report2": ["IFRC", "WHO", "CNN"],
    "Report3": ["UNHCR", "BBC"],
    "Report4": ["WHO", "IFRC"],
    "Report5": ["UNICEF", "CNN"],
    "Report6": ["IFRC", "UNHCR", "BBC"],
    "Report7": ["WHO", "BBC", "CNN"],
}

# Extract unique nodes
reports = list(report_agency_data.keys())
agencies = list(set(agency for ag_list in report_agency_data.values() for agency in ag_list))

# Create bipartite graph
B = nx.Graph()

# Add nodes with bipartite attribute
B.add_nodes_from(reports, bipartite=0)
B.add_nodes_from(agencies, bipartite=1)

# Add edges: agency involved in a report
for report, ag_list in report_agency_data.items():
    for agency in ag_list:
        B.add_edge(report, agency)

# Visualize bipartite graph
plt.figure(figsize=(10, 6))
pos = nx.spring_layout(B, seed=42)
nx.draw(B, pos, with_labels=True, node_color=["skyblue" if n in reports else "lightgreen" for n in B.nodes()])
plt.title("Bipartite Graph: Reports and Agencies")
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


### TODO CHANGE THIS ALSO!!!
# ---------------------------
# Dummy Role Assignment for Assortativity
# ---------------------------
role_map = {
    "WHO": "responder",
    "UNICEF": "donor",
    "BBC": "media",
    "IFRC": "responder",
    "CNN": "media",
    "UNHCR": "responder"
}
nx.set_node_attributes(agency_proj, role_map, "role")

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
