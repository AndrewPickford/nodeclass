## Introduction

Nodeclass is a reimplementation of the extended version of Reclass (insert link to extended and original). The extended version
added inventory queries, nested references, escaping the reference token (the dollar-curly-brace). The reimplementation
brings significant performance gains for inventory queries and a slight performance gain overall.

The goal was to improve readability and maintainability of the code base.

## High level overview (for developers)

The interpolator (for a node):
- starts by merging together all the exports
- then all of the parameters;
- then it figures out what the inventory queries are;
- it evaluates all the inventory queries;
- it works out all of the nodes references and then
- it evaluates all the exports
- returns the data

## Glossary

* Interpolate: Merge down all the data for the node and classes and resolving all the references and inventory queries.
* Inventory query: marked by dollar-square-bracket, takes data from other nodes' exports 
* Reference: data taken from another parameter path using dollar-curly-brace notation
* Path: 
* Context: thread-local storage of configuration settings that control behaviour at low level
* Klass loader: takes care of loading classes from some (set of) URI(s) and presenting it to the interpolator in a standard way
* Node loader: same for the node files  
* Hierarchy: top-level dictionary like parameters or exports
