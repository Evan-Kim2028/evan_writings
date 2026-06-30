---
title: "Applications of Graph Theory on the Structure of a DAO"
date: "2021-11-01"
collection: defi
tags:
  - writing
  - defi
  - mirror
source_url: https://mirror.xyz/evandekim.eth/fuznGoiFzMmDk6iMdunDejkPiuRbJ5yqDRzg7-q2IYA
source_platform: mirror
slug: applications-of-graph-theory-on-the-structure-of-a-dao
---

## Graph Representation of a DAO

An organization can be represented as a graph by allowing each node to be a department and each edge to be a shared responsibility between two departments.

In the above example, the following nodes are operations, treasury, sales, and marketing, and two miscellaneous departments. Notice that there is a connection between every node. This type of graph is called a [complete graph](https://mathworld.wolfram.com/CompleteGraph.html#:~:text=A%20complete%20graph%20is%20a,are%20sometimes%20called%20universal%20graphs.) or fully connected. If any node is removed, the graph will still remain complete. In other words, none of the functions of the remaining nodes will be affected because the graph is still a complete graph, which can be seen as an equivalent definition for ‘decentralization’.

![Example - Complete Graph of a DAO, maximally decentralized](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/7b51e28713d69a8ecc214d2d3e0c55ed3bdc263d41bc5c6a2c17dab9a4e199e4.jpg)

Example - Complete Graph of a DAO, maximally decentralized

An observation about complete graphs is that a complete graph also represents a maximally decentralized graph. To see why this is true, consider the following graph below to the left, which is a connected graph, but not complete. Notice that the operations node is the gateway in which all the other nodes are connected. Thus the operations node makes this graph very centralized. If the operations node is removed, the organization will cease to function properly and the graph will no longer be a connected graph as seen below to the right. 

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/0e71ddb57d05fbbce4cbbd9c7a2e0f23f51e46e39bd418f0d5c507525b238b45.jpg)

## Maximal Decentralization in a Graph

Viewing the organizational structure of a DAO or any organization through the lens of graph theory gives us the additional benefit of being able to quantify how much centralization or decentralization exists within a DAO. As DAO’s continue to figure out the daoification process, the end goal will be towards a maximally decentralized DAO structure, or a complete graph structure. The more decentralized a DAO becomes, the more robust it will be to new organizational changes over time. 

## Understanding Department Responsibilities and Functions within a DAO

We can use the graph structure to describe the complexities of a DAO. For example consider this sample DAO structure represented as a graph:

![post image](https://img.paragraph.com/cdn-cgi/image/format=auto,width=3840,quality=85/https://storage.googleapis.com/papyrus_images/4e1e48f20f3ef5c1f583b2a00a6d6b92ef036e235e3d5a1a59cdc4adc3565369.jpg)

Although not a complete graph, we can immediately see the level of decentralization each department has based on the number of edges that belong to the node. The more edges a node has, the more ‘reliant’ the entire DAO will be on that node. A higher number of total edges in the graph implies an overall higher level of decentralization. 

Another use case is to chart the paths from one node to another. For example there is no direct edge between the sales and treasury nodes. The shortest paths, both of length 2, are 

sales -> marketing -> treasury

sales -> operations -> treasury

Additional questions can then be asked whether there should indeed be a direct connection between sales and treasury or not. Is a 2 edge path sufficient or do sales and treasury responsibilities overlap so much that there should be an edge established directly between sales and treasury? We would also expect that the sales department will have the most overlapping responsibilities with operations and marketing departments and have no direct overlapping responsibilities with new department1, new department 2, and treasury. 

## Conclusion

Using graph theory to understand the structure of a DAO to characterize the levels of decentralization can offer valuable insights and guide a DAO through the daofication process. Adding/removing new departments to the DAO via nodes to a graph makes the process quantitative and offers additional insight to the responsibilities and functions of the departments and shows which responsibilities overlap and which responsibilities are independent.
