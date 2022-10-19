import copy
import json
import os
from pathlib import Path
from lxml import etree
from lxml.etree import _Element, _Attrib, _ElementTree


class HaloXML:
    """
    Class around the halo .annotations files.
    """

    def __init__(self) -> None:
        self.pth = Path()  # type: Path
        self.tree = etree.Element("root")  # type:_ElementTree
        self.regions = []  # type:[Region]
        self.valid = False  # type:bool

    def __bool__(self) -> bool:
        return self.valid

    def load(self, pth: os.PathLike | str) -> None:
        """
        Load .annotations file
        :param pth:
        :return:
        """
        self.pth = Path(pth)
        self.tree = etree.parse(pth)
        annotations = self.tree.getroot().getchildren()
        for annotation in annotations:
            regions = annotation.getchildren()[0]
            for region in regions:
                self.regions.append(Region(region, annotation.attrib))
        self.valid = True

    def getannotationattributes(self) -> list:
        """
        Get all unique annotation attributes
        :return: dictionary with unique annotation attributes
        """
        unique_attrs = set([json.dumps(d.annatr, sort_keys=True) for d in self.regions])
        return [json.loads(x) for x in unique_attrs]

    def groupregions(self) -> dict:
        """
        group regions based on annotation attributes
        :return: a dictionary where the key is the unique attributes
        """
        grouped_regions = {}
        for r in self.regions:
            attr = json.dumps(r.annatr, sort_keys=True)
            if attr in grouped_regions.keys():
                grouped_regions[attr].append(r)
            else:
                grouped_regions[attr] = [r]
        return grouped_regions

    def save(self, pth: os.PathLike | str) -> None:
        """
        Group regions based on annotation attributes
        :param pth: path to save the annotations to
        :return:
        """
        annotations = self.groupregions()
        new_root = etree.Element("Annotations")
        for annotation in annotations:
            anno = etree.Element("Annotation", json.loads(annotation))
            for region in annotations[annotation]:
                anno.append(region.region)
            new_root.append(anno)
        pth = Path(pth)
        if not pth.suffix:
            pth = Path(pth.parent, pth.name + ".annotations")
        with open(pth, "wb") as f:
            f.write(etree.tostring(new_root))


class Region:
    def __init__(self, region: _Element, annotationattribs: _Attrib) -> None:
        self.region = region  # type: _Element
        self.annatr = copy.deepcopy(annotationattribs)  # type: _Attrib

    def getvertices(self) -> _Element:
        """
        Get the vertices of the region
        :return: the vertices element
        """
        for e in self.region.getchildren():
            if e.tag == "Vertices":
                return e
