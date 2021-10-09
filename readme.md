readme

Concrete dam stability
===

&copy; timsta95, 2021

## Stability analyses of buttress dams and gravity dams, adapted for Norway and NVE's guidelines

*IMPORTANT: ALTHOUGH TESTED AND USED FOR REAL-WORLD APPLICATIONS, THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, SEE LICENSE FILE (MIT LICENSE)*

The creation and maintenance of this package is a solely private initiative

---

## 1. About the project
The goal of the project is to provide a flexible and reliable tool for stability analyses of concrete dams. Calculations can be documented as PDF report including graphic representations of static forces. Furthermore, the GitHub repository provides [tools](https://github.com/timsta95/stabilipy/tree/master/dynamo) for 3D visualisations of results with [Autodesk Civil 3D Dynamo](https://knowledge.autodesk.com/support/civil-3d/learn-explore/caas/CloudHelp/cloudhelp/2020/ENU/Civil3D-UserGuide/files/GUID-E2122814-1957-4108-9BBF-0AD6AF1A63CB-htm.html) (proprietary software).

Safety factors and procedures are adapted to the requirements of the [Norwegian Water Resources and Energy Directorate](https://nve.no/) (NVE). The evaluated modes of failure are:
- sliding
- overturning

For usage outside of Norway, safety factors can be changed.

## 2. How to get started
The package can be installed from [PyPI](https://pypi.org/project/stabilipy/) with
```python
pip install stabilipy
```
Examples for a dam setup, export of results to Dynamo and creating a report can be found in the [*tests*](https://github.com/timsta95/stabilipy/tree/master/tests) folder of the GitHub repository. 

## 3. Support and project maintenance
The package is under active development. The author of the package can be contacted via GitHub or [e-mail](mailto:stabilipy@gmail.com).

Contribution is encouraged

## 4. To do
- add documentation
- add tests
- add downstream water table
- add cohesion
- add \__repr__ and \__add__ methods where useful
- bug hunt



