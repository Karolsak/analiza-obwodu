import schemdraw
import schemdraw.elements as elm
import os
from warnings import warn
from lcapy import Circuit
from lcapy import NetlistLine
from typing import List
from lcapy.impedanceConverter import ImpedanceToComponent
from lcapy.impedanceConverter import getSourcesFromCircuit, getOmegaFromCircuit
from lcapy.unitWorkAround import UnitWorkAround as uwa
from sympy import latex
from sympy import sympify
from lcapy.unitPrefixer import SIUnitPrefixer
from lcapy.jsonExportBase import JsonExportBase


class DrawWithSchemdraw:
    """
    Use the schemdraw package to draw a netlist generated with lcapy
    """
    def __init__(self, circuit: Circuit, fileName: str = "circuit", removeDangling: bool = True):
        """
        Use the schemdraw package to draw a netlist generated with lcapy. Only supports svg-files as output
        :param circuit: lcapy.Circuit object
        :param fileName: name for the generated file, standard is circuit.svg
        created pictures will be named by step e.g.: circuit_step0.svg
        """
        self.nodePos = {}
        self.cirDraw = schemdraw.Drawing()

        self.omega_0 = getOmegaFromCircuit(circuit, getSourcesFromCircuit(circuit))

        if removeDangling:
            self.netlist = (circuit.remove_dangling()).netlist()
        else:
            self.netlist = circuit.netlist()

        self.netLines: List[NetlistLine] = []
        self.fileName = os.path.splitext(fileName)[0]
        self.invertDrawParam = {"up": "down", "down": "up", "left": "right", "right": "left"}

        # elm.style(elm.STYLE_IEC)
        # TODO would be nice to dont need this
        # print("Enforce svg backend")
        schemdraw.use(backend='svg')

        for line in self.netlist.splitlines():
            self.netLines.append(NetlistLine(line))

        self.prefixer = SIUnitPrefixer()
        self.jsonExportBase = JsonExportBase(precision=3)

    def latexStr(self, line: NetlistLine):
        if line.value is None or line.type is None:
            return None
        else:
            return self.jsonExportBase.latexWithPrefix(uwa.addUnit(line.value, line.type))

    def addNodePositions(self, netLine: NetlistLine):
        if netLine.startNode not in self.nodePos.keys():
            self.nodePos[netLine.startNode] = self.cirDraw.elements[-1].start
        if netLine.endNode not in self.nodePos.keys():
            self.nodePos[netLine.endNode] = self.cirDraw.elements[-1].end

    def addElement(self, element: schemdraw.elements, netLine: NetlistLine):

        label = netLine.label()

        # if no node position is known this is the first element it is used as the start points
        if netLine.startNode not in self.nodePos.keys() and netLine.endNode not in self.nodePos.keys():
            self.cirDraw.add(element.label(label))
        # if both node positions are known draw the element between them
        elif netLine.startNode in self.nodePos and netLine.endNode in self.nodePos.keys():
            self.cirDraw.add(
                element.label(label).endpoints(
                    self.nodePos[netLine.startNode],
                    self.nodePos[netLine.endNode]
                )
            )
        # if only the start node is known draw from there
        elif netLine.startNode in self.nodePos.keys():
            self.cirDraw.add(element.label(label).at(self.nodePos[netLine.startNode]))
        # if only the end node is known invert the direction information and start at the end node
        else:
            try:
                element._userparams['d'] = self.invertDrawParam[netLine.drawParam]
                self.cirDraw.add(element.label(label).at(self.nodePos[netLine.endNode]))
            except KeyError:
                raise RuntimeError(f"unknown drawParam {netLine.drawParam}")

        self.addNodePositions(netLine)

    @staticmethod
    def orderNetlistLines(netLines: list[NetlistLine]):
        """
        order the netlist so that the nodes are in a drawable sequence. The drawing process relies on defined node
        positions that are only known if it already has drawn to this node.
        E.g. 1:
        R1 2 3; left
        R2 3 4; left
        R3 4 5; left -> works
        E.g. 2:
        R1 2 3; left
        R3 4 5; left
        R2 3 4; left -> does not work
        this function reorders E.g. 2 into E.g 1
        :return: void, list is reordered in place
        """
        netLines.sort(key=lambda x: x.startNode)

    def draw(self, path=None):
        DrawWithSchemdraw.orderNetlistLines(self.netLines)




        # save the created svg file
        if os.path.splitext(self.fileName)[1] == ".svg":
            saveName = self.fileName
        else:
            saveName = self.fileName + ".svg"
        self.cirDraw.save(saveName)

        if path:
            newPath = os.path.join(path, saveName)
            if os.path.exists(newPath):
                os.remove(newPath)
            os.rename(saveName, newPath)
            return newPath

        return saveName
    def draw_element(self, line: NetlistLine):
        value = None
        if line.type == "Z":
            line = NetlistLine(ImpedanceToComponent(netlistLine=line, omega_0=self.omega_0))
            value = self.latexStr(line)
        id_ = line.label()
        if line.type == "R" or line.type == "Z":
            self.addElement(elm.Resistor(id_=id_, value_=value, d=line.drawParam), line)
        elif line.type == "L":
            self.addElement(elm.Resistor(id_=id_, value_=value, d=line.drawParam, fill=True), line)
        elif line.type == "C":
            self.addElement(elm.Capacitor(id_=id_, value_=value, d=line.drawParam), line)
        elif line.type == "W":
            self.addElement(elm.Line(d=line.drawParam), line)
        elif line.type == "V":
            if line.ac_dc == "ac":
                self.addElement(elm.sources.SourceSin(id_=id_, value_=value, d=line.drawParam), line)
            elif line.ac_dc == "dc":
                self.addElement(elm.sources.SourceV(id_=id_, value_=value, d=line.drawParam), line)
        elif line.type == "I":
            if line.ac_dc == "ac":
                self.addElement(elm.sources.SourceI(id_=id_, value_=value, d=line.drawParam), line)
            elif line.ac_dc == "dc":
                self.addElement(elm.sources.SourceI(id_=id_, value_=value, d=line.drawParam), line)

        else:
            raise RuntimeError(f"unknown element type {line.type}")

    def add_connection_dots(self):
        """
        adds the dots that are on connections between two lines e.g when a line splits up in two lines a dot is created
        at the split point
        :return: does not return anything
        """
        # count the occurrences of each node and if it is greater than 2 set a dot
        counts = {}
        for line in self.netLines:
            counts[line.startNode] = counts.get(line.startNode, 0) + 1
            counts[line.endNode] = counts.get(line.endNode, 0) + 1
        for node in counts.keys():
            if counts[node] > 2:
                self.cirDraw.add(elm.Dot().at(self.nodePos[node]))
