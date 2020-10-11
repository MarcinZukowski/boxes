#!/usr/bin/env python3
# Copyright (C) 2013-2020 Florian Festi
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from boxes import *
import copy

class CornerBox(Boxes):
    """Triangular box to put in a corner"""

    ui_group = "Box"

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings)
        self.buildArgParser("h", "outside")
        self.argparser.add_argument(
            "--depth",  action="store", type=float, default=100.0,
            help="side wall depth (in mm)")
        self.argparser.add_argument(
            "--angle",  action="store", type=float, default=90,
            help="corner angle (in degrees)")
        self.argparser.add_argument(
            "--top",  action="store", type=str, default="none",
            choices=["none", "lid", "closed"],
            help="style of the top")
        self.argparser.add_argument(
            "--inverse",  action="store", type=boolarg, default=False,
            help="inverse the finger directions")
        self.argparser.add_argument(
            "--wide_front", action="store", type=boolarg, default=False,
            help="wide front (no fingers on edges)")


    def triangularWall(self, side1, angle1, side2, angle2, side3, edges="eee",
                           callback=None, move=None):
        """
        Triangular wall

        :param side1, side2, side3 - side lengths in mm
        :param angle1, angle2 - angles between side1/2 and side2/3, resp.
        :param edges:  (Default value = "eee") types of edges counterclockwise
        :param callback:  (Default value = None)
        :param move:  (Default value = None)

        """

        edges = [self.edges.get(e, e) for e in edges]

        angle3 = 180 - angle1 - angle2

        # TODO: Compute these properly
        overallwidth = side1 * 1.5
        overallheight = side3 * 1.5

        if self.move(overallwidth, overallheight, move, before=True):
            return

        self.moveTo(edges[-1].spacing(), edges[0].margin())
        self.cc(callback, 0, y=edges[0].startwidth())
        edges[0](side1)
        self.edgeCorner(edges[0], edges[1], angle=180 - angle1)
        self.cc(callback, 1, y=edges[1].startwidth())
        edges[1](side2)
        self.edgeCorner(edges[1], edges[2], angle=180 - angle2)
        self.cc(callback, 2)
        edges[2](side3)
        self.edgeCorner(edges[-1], edges[0], 180 - angle3)

        self.move(overallwidth, overallheight, move)

    def front_width(self, depth, angle):
        return (depth ** 2 * 2 * (1 - math.cos(math.radians(angle)))) ** 0.5

    def render_base(self, depth, angle, edge, move='right', callback=None):
        # Front side width
        front = self.front_width(depth, angle)

        angle2 = (180 - angle) / 2

        self.triangularWall(depth, angle2, front, angle2, depth, edges=3 * edge, move=move, callback=callback)

    def render(self):

        depth, h, angle, inverse, wide_front = self.depth, self.h, self.angle, self.inverse, self.wide_front

        # Determine edge types based on settings
        base_edge = 'F' if inverse else 'f'
        bottom_edge = 'f' if inverse else 'F'
        top_edge = bottom_edge if self.top in ("closed") else 'e'
        side_vertical_edge = 'e' if wide_front else 'g'
        front_vertical_edge = 'E' if wide_front else 'G'

        # TODO: Handle outside

        # Draw the base walls
        with self.saved_context():
            # Base
            self.render_base(depth, angle, base_edge)

            # Lids
            if self.top == "lid":
                self.render_base(depth, angle, 'e')
                self.render_base(depth, angle, 'E')
            elif self.top == "closed":
                self.render_base(depth, angle, base_edge)

        fingerJointSettings = copy.deepcopy(self.edges["f"].settings)
        fingerJointSettings.setValues(self.thickness, angle=90)  # TODO: what angle should this be?
        fingerJointSettings.edgeObjects(self, chars="gGH")

        # Draw the side walls
        self.rectangularWall(depth, h, move="down right",
                             edges=bottom_edge + 'g' + top_edge + side_vertical_edge)
        self.rectangularWall(depth, h, move="right",
                             edges=bottom_edge + 'G' + top_edge + side_vertical_edge)

        # Draw the front wall
        front = self.front_width(depth, angle)
        self.rectangularWall(front, h, move="right",
                             edges=bottom_edge + front_vertical_edge + top_edge + front_vertical_edge)
