# PCB Netlist Visualizer + Validator
![img.png](docs/img.png)
## Task

Build a small, proof-of-concept application which lets users:

### 1. Upload a simple [netlist](https://en.wikipedia.org/wiki/Netlist) file formatted as JSON
- **a.** Schema is yours to define
- **b.** Must list components w/ pins
- **c.** Must list nets
- **d.** Must specify connections between nets and components

### 2. Visualize (SVG, Canvas, etc) the netlist as a graph where:
- **a.** Nodes are components (ICs, resistors, connectors, etc)
- **b.** Edges are electrical connections (nets)

### 3. Validate submitted netlist data conforms to a series of basic rules like:
- **a.** **Name** data must not be blank
- **b.** **GND** must be connected to all relevant components

### 4. Store submissions in a database (e.g. MongoDB)

### 5. Display list of submissions per-user

### 6. Display validation results per-submission, highlighting violations

## Requirements

- **Must use client ↔ server architecture**
- **Must run locally to facilitate live development and review**
- **Must be deployable + runnable in common cloud hosting services (e.g. AWS) using a docker container**

---

*Note: This is an example prompt and is not authoritative.*
