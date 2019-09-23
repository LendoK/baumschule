# -*- coding: utf-8 -*-
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Baumschule",
    "author": "Andrew Hale (TrumanBlending), Aaron Buchler, Lendo Keilbaum",
    "version": (1, 1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Curve",
    "description": ("Adds a parametric tree. The method is presented by "
    "Jason Weber & Joseph Penn in their paper 'Creation and Rendering of "
    "Realistic Trees'. Modifikation by Lendo Keilbaum"),
    "category": "Add Mesh"}

if "bpy" in locals():
    import importlib
    importlib.reload(bs_utils)
else:
    from baumschule import bs_utils

import bpy
import bpy.utils.previews
import time
import os
import ast

# import cProfile

from bpy.types import (
        Operator,
        Menu,
        Panel,
        )
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        FloatVectorProperty,
        IntProperty,
        IntVectorProperty,
        StringProperty,
        )

useSet = False
# global variable to store icons in
custom_icons = None

shapeList = [('0', 'Conical (0)', 'Shape = 0'),
            ('1', 'Spherical (1)', 'Shape = 1'),
            ('2', 'Hemispherical (2)', 'Shape = 2'),
            ('3', 'Cylindrical (3)', 'Shape = 3'),
            ('4', 'Tapered Cylindrical (4)', 'Shape = 4'),
            ('5', 'Flame (5)', 'Shape = 5'),
            ('6', 'Inverse Conical (6)', 'Shape = 6'),
            ('7', 'Tend Flame (7)', 'Shape = 7')]

shapeList3 = [('0', 'Conical', ''),
            ('6', 'Inverse Conical', ''),
            ('1', 'Spherical', ''),
            ('2', 'Hemispherical', ''),
            ('3', 'Cylindrical', ''),
            ('4', 'Tapered Cylindrical', ''),
            ('10', 'Inverse Tapered Cylindrical', ''),
            ('5', 'Flame', ''),
            ('7', 'Tend Flame', ''),
            ('8', 'Custom Shape', '')]

shapeList4 = [('0', 'Conical', ''),
            ('6', 'Inverse Conical', ''),
            ('1', 'Spherical', ''),
            ('2', 'Hemispherical', ''),
            ('3', 'Cylindrical', ''),
            ('4', 'Tapered Cylindrical', ''),
            ('10', 'Inverse Tapered Cylindrical', ''),
            ('5', 'Flame', ''),
            ('7', 'Tend Flame', '')]

handleList = [('0', 'Auto', 'Auto'),
                ('1', 'Vector', 'Vector')]

settings = [('0', 'Geometry', 'Geometry'),
            ('1', 'Branch Radius', 'Branch Radius'),
            ('2', 'Branch Splitting', 'Branch Splitting'),
            ('3', 'Branch Growth', 'Branch Growth'),
            ('4', 'Leaves', 'Leaves')]

            # ('5', 'Pruning', 'Pruning'),
            # ('6', 'Armature', 'Armature'),
            # ('7', 'Animation', 'Animation')]

branchmodes = [("original", "Original", "rotate around each branch"),
              ("rotate", "Rotate", "evenly distribute  branches to point outward from center of tree"),
              ("random", "Random", "choose random point")]


def getPresetpath():
    """Support user defined scripts directory
       Find the first occurrence of add_curve_sapling/presets in possible script paths
       and return it as preset path"""

    script_file = os.path.realpath(__file__)
    directory = os.path.dirname(script_file)
    directory = os.path.join(directory, "presets")
    return directory


def getPresetpaths():
    """Return paths for both local and user preset folders"""
    userDir = os.path.join(bpy.utils.script_path_user(), 'presets', 'operator', 'baumschule')

    if os.path.isdir(userDir):
        pass
    else:
        os.makedirs(userDir)

    script_file = os.path.realpath(__file__)
    directory = os.path.dirname(script_file)
    localDir = os.path.join(directory, "presets")

    return (localDir, userDir)


class ExportData(Operator):
    """This operator handles writing presets to file"""
    bl_idname = 'baumschule.exportdata'
    bl_label = 'Export Preset'

    data: StringProperty()

    def execute(self, context):
        # Unpack some data from the input
        filename, overwrite = eval(self.data)
        data_dict = context.active_object.tree_props.get_property_dict()
        data = str(data_dict)
        """
        try:
            # Check whether the file exists by trying to open it.
            f = open(os.path.join(getPresetpaths()[1], filename + '.py'), 'r')
            f.close()
            # If it exists then report an error
            self.report({'ERROR_INVALID_INPUT'}, 'Preset Already Exists')
            return {'CANCELLED'}
        except IOError:
            if data:
               # If it doesn't exist, create the file with the required data
               f = open(os.path.join(getPresetpaths()[1], filename + '.py'), 'w')
               f.write(data)
               f.close()
               return {'FINISHED'}
        else:
            return {'CANCELLED'}
        """
        fpath1 = os.path.join(getPresetpaths()[0], filename + '.py')
        fpath2 = os.path.join(getPresetpaths()[1], filename + '.py')

        if os.path.exists(fpath1):
            # If it exists in built-in presets then report an error
            self.report({'ERROR_INVALID_INPUT'}, 'Can\'t have same name as built-in preset')
            return {'CANCELLED'}
        elif (not os.path.exists(fpath2)) or (os.path.exists(fpath2) and overwrite):
            # if (it does not exist) or (exists and overwrite) then write file
            if data:
                # If it doesn't exist, create the file with the required data
                f = open(os.path.join(getPresetpaths()[1], filename + '.py'), 'w')
                f.write(data)
                f.close()
                return {'FINISHED'}
            else:
                return {'CANCELLED'}
        else:
            # If it exists then report an error
            self.report({'ERROR_INVALID_INPUT'}, 'Preset Already Exists')
            return {'CANCELLED'}


class ImportData(Operator):
    """This operator handles importing existing presets"""
    bl_idname = "baumschule.importdata"
    bl_label = "Import Preset"

    filename: StringProperty()

    def execute(self, context):
        # Make sure the operator knows about the global variables
        global settings, useSet
        # Read the preset data into the global settings
        try:
            f = open(os.path.join(getPresetpaths()[0], self.filename), 'r')
        except (FileNotFoundError, IOError):
            f = open(os.path.join(getPresetpaths()[1], self.filename), 'r')
        settings = f.readline()
        f.close()
        # print(settings)
        settings = ast.literal_eval(settings)

        # use old attractup
        if type(settings['attractUp']) == float:
            atr = settings['attractUp']
            settings['attractUp'] = [0, 0, atr, atr]

        # use old leaf rotations
        if 'leafDownAngle' not in settings:
            l = settings['levels']
            settings['leafDownAngle'] = settings['downAngle'][min(l, 3)]
            settings['leafDownAngleV'] = settings['downAngleV'][min(l, 3)]
            settings['leafRotate'] = settings['rotate'][min(l, 3)]
            settings['leafRotateV'] = settings['rotateV'][min(l, 3)]

        # zero leaf bend
        settings['bend'] = 0

        # Set the flag to use the settings
        useSet = True
        context.active_object.tree_props.load_settings(context)
        return {'FINISHED'}


class PresetMenu(Menu):
    """Create the preset menu by finding all preset files
    in the preset directory"""
    bl_idname = "BAUMSCHULE_MT_preset"
    bl_label = "Presets"

    def draw(self, context):
        # Get all the sapling presets
        presets = [a for a in os.listdir(getPresetpaths()[0]) if a[-3:] == '.py']
        presets.extend([a for a in os.listdir(getPresetpaths()[1]) if a[-3:] == '.py'])
        layout = self.layout
        # Append all to the menu
        for p in presets:
            layout.operator("baumschule.importdata", text=p[:-3]).filename = p

class NewTree(Operator):
    bl_idname = "mesh.newtree"
    bl_label = "Baumschule: Spawn New Tree"
    bl_options = {'REGISTER'}
    bl_description="plant a new tree"

    def execute(self, context):

        # for ob in bpy.data.objects:
        #     ob.select_set(False)
        bpy.ops.object.select_all(action='DESELECT')

        # Initialise the tree object and curve and adjust the settings
        cu = bpy.data.curves.new('tree', 'CURVE')
        treeOb = bpy.data.objects.new('tree', cu)
        bpy.context.scene.collection.objects.link(treeOb)
        treeOb.location = context.scene.cursor.location

        treeOb.select_set(True)
        bpy.context.view_layer.objects.active = treeOb
        treeOb.tree_props.istree = True
        bs_utils.addTree(treeOb)
        return{'FINISHED'}

class AddTree(Panel):
    bl_idname = "PANEL_PT_tree_add"
    bl_space_type = "VIEW_3D"
    bl_label = "Baumschule:"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"


    def draw(self, context):
        row = self.layout.row()
        row.label(text="", icon_value=custom_icons["custom_icon"].icon_id)
        if context.active_object and context.active_object.select_get() and context.active_object.tree_props.istree:
            context.object.tree_props.draw(self.layout)
        col = self.layout.column(align=True)
        self.layout.operator("mesh.newtree", text='create new Tree')


class tree_tree_props(bpy.types.PropertyGroup):
    global custom_icons
    def objectList(self, context):
        objects = []
        bObjects = bpy.data.objects

        for obj in bObjects:
            if (obj.type in ['MESH', 'CURVE', 'SURFACE']) and (obj.name not in ['tree', 'leaves']):
                objects.append((obj.name, obj.name, ""))

        return (objects if objects else
                [('NONE', "No objects", "No appropriate objects in the Scene")])

    def update_tree(self, context):
        if not useSet:
            bs_utils.addTree(context.object)

    def update_leaf_shape(self, context):
        if self.leafShape != "dVert":
            self.update_leaves(context)

    def update_leaves(self, context):
        if self.showLeaves and not useSet:
            bs_utils.addTree(context.object)

    def no_update_tree(self, context):
        # self.do_update = False
        pass


    def load_settings(self, context):
        global settings, useSet
        if useSet:
            self.showLeaves = False
            for a, b in settings.items():
                # print("prop: {0}, wert: {1}".format(a, b))
                if hasattr(self, a):
                    setattr(self, a, b)
                else:
                    print("could not set missing prop: {0}, value {1}".format(a, b))
            if self.limitImport:
                setattr(self, 'levels', min(settings['levels'], 2))
                setattr(self, 'showLeaves', False)
        self.bevel = True
        bs_utils.addTree(context.object)
        useSet = False

    istree: BoolProperty(
        name='istree',
        default=False, options={'HIDDEN'}
        )

    do_update: BoolProperty(
        name='Do Update',
        default=True, options={'HIDDEN'}
        )

    chooseSet: EnumProperty(
        name='Settings',
        description='Choose the settings to modify',
        items=settings,
        default='0', update=no_update_tree
        )
    bevel: BoolProperty(
        name='Bevel',
        description='Whether the curve is beveled',
        default=True, update=update_tree
        )
    prune: BoolProperty(
        name='Prune',
        description='Whether the tree is pruned',
        default=False, update=update_tree
        )
    showLeaves: BoolProperty(
        name='Show Leaves',
        description='Whether the leaves are shown',
        default=False, update=update_tree
        )
    useArm: BoolProperty(
        name='Use Armature',
        description='Whether the armature is generated',
        default=False, update=update_tree
        )
    seed: IntProperty(
        name='Random Seed',
        description='The seed of the random number generator',
        default=0, update=update_tree
        )
    handleType: IntProperty(
        name='Handle Type',
        description='The type of curve handles',
        min=0,
        max=1,
        default=0, update=update_tree
        )
    levels: IntProperty(
        name='Levels',
        description='Number of recursive branches (Levels)',
        min=1,
        max=4,
        default=3, update=update_tree
        )
    length: FloatVectorProperty(
        name='Length',
        description='The relative lengths of each branch level (nLength)',
        min=0.000001,
        max=1.0,
        default=[1, 0.3, 0.6, 0.45],
        size=4, update=update_tree
        )
    lengthV: FloatVectorProperty(
        name='Length Variation',
        description='The relative length variations of each level (nLengthV)',
        min=0.0001,
        max=1.0,
        default=[0, 0, 0, 0],
        size=4, update=update_tree
        )
    rotateUV: BoolProperty(
        name='rotateUV',
        description='rotates uv set',
        default=False, update=update_tree
    )
    UVSize: FloatVectorProperty(
        name='UVScale',
        description='UV Coordinatis Size',
        min=0.0,
        max=100.0,
        default=[1, 1],
        size=2, update=update_tree
        )
    taperCrown: FloatProperty(
        name='Taper Crown',
        description='Shorten trunk splits toward outside of tree',
        min=0.0,
        soft_max=1.0,
        default=0, update=update_tree
        )
    branches: IntVectorProperty(
        name='Branches',
        description='The number of branches grown at each level (nBranches)',
        min=0,
        max=30,
        default=[50, 30, 10, 10],
        size=4, update=update_tree
        )
    curveRes: IntVectorProperty(
        name='Curve Resolution',
        description='The number of segments on each branch (nCurveRes)',
        min=1,
        max=10,
        default=[3, 5, 3, 1],
        size=4, update=update_tree
        )
    deadBranch_C: FloatVectorProperty(
        name='Dead Brach chance',
        description='how likely the brach is dead',
        min=0.0,
        max=1.0,
        default=[0.0, 0.0, 0.0, 0.0],
        size=4, update=update_tree
        )
    curve: FloatVectorProperty(
        name='Curvature',
        description='The angle of the end of the branch (nCurve)',
        default=[0, -40, -40, 0],
        size=4, update=update_tree
        )
    curveV: FloatVectorProperty(
        name='Curvature Variation',
        description='Variation of the curvature (nCurveV)',
        default=[20, 50, 75, 0],
        size=4, update=update_tree
        )
    curveBack: FloatVectorProperty(
        name='Back Curvature',
        description='Curvature for the second half of a branch (nCurveBack)',
        default=[0, 0, 0, 0],
        size=4, update=update_tree
        )
    baseSplits: IntProperty(
        name='Base Splits',
        description='Number of trunk splits at its base (nBaseSplits)',
        min=0,
        max=10,
        default=0, update=update_tree
        )
    segSplits: FloatVectorProperty(
        name='Segment Splits',
        description='Number of splits per segment (nSegSplits)',
        min=0,
        max=6,
        soft_max=3,
        default=[0, 0, 0, 0],
        size=4, update=update_tree
        )
    splitByLen: BoolProperty(
        name='Split relative to length',
        description='Split proportional to branch length',
        default=False, update=update_tree
        )
    rMode: EnumProperty(
        name="",  # "Branching Mode"
        description='Branching and Rotation Mode',
        items=branchmodes,
        default="rotate", update=update_tree
        )
    splitAngle: FloatVectorProperty(
        name='Split Angle',
        description='Angle of branch splitting (nSplitAngle)',
        default=[0, 0, 0, 0],
        size=4, update=update_tree
        )
    splitAngleV: FloatVectorProperty(
        name='Split Angle Variation',
        description='Variation in the split angle (nSplitAngleV)',
        default=[0, 0, 0, 0],
        size=4, update=update_tree
        )
    scale: FloatProperty(
        name='Scale',
        description='The tree scale (Scale)',
        min=0.0,
        default=13.0, update=update_tree)
    scaleV: FloatProperty(name='Scale Variation',
        description='The variation in the tree scale (ScaleV)',
        default=3.0, update=update_tree
        )
    attractUp: FloatVectorProperty(
        name='Vertical Attraction',
        description='Branch upward attraction',
        default=[0, 0, 0, 0],
        size=4, update=update_tree
        )
    attractOut: FloatVectorProperty(
        name='Outward Attraction',
        description='Branch outward attraction',
        default=[0, 0, 0, 0],
        min=0.0,
        max=1.0,
        size=4, update=update_tree
        )
    shape: EnumProperty(
        name='Shape',
        description='The overall shape of the tree (Shape)',
        items=shapeList3,
        default='7', update=update_tree
        )
    shapeS: EnumProperty(
        name='Secondary Branches Shape',
        description='The shape of secondary splits',
        items=shapeList4,
        default='4', update=update_tree
        )
    customShape: FloatVectorProperty(
        name='Custom Shape',
        description='custom shape branch length at (Base, Middle, Middle Position, Top)',
        size=4,
        min=.01,
        max=1,
        default=[.5, 1.0, .3, .5], update=update_tree
        )
    branchDist: FloatProperty(
        name='Branch Distribution',
        description='Adjust branch spacing to put more branches at the top or bottom of the tree',
        min=0.1,
        soft_max=10,
        default=1.0, update=update_tree
        )
    nrings: IntProperty(
        name='Branch Rings',
        description='grow branches in rings',
        min=0,
        default=0, update=update_tree
        )
    baseSize: FloatProperty(
        name='Trunk Height',
        description='Fraction of tree height with no branches (Base Size)',
        min=0.0,
        max=1.0,
        default=0.4, update=update_tree
        )
    baseSize_s: FloatProperty(
        name='Secondary Base Size',
        description='Factor to decrease base size for each level',
        min=0.0,
        max=1.0,
        default=0.25, update=update_tree
        )
    splitHeight: FloatProperty(
        name='Split Height',
        description='Fraction of tree height with no splits',
        min=0.0,
        max=1.0,
        default=0.2, update=update_tree
        )
    splitBias: FloatProperty(
        name='splitBias',
        description='Put more splits at the top or bottom of the tree',
        default=0.0, update=update_tree
        )
    ratio: FloatProperty(
        name='Ratio',
        description='Base radius size (Ratio)',
        min=0.0,
        default=0.015, update=update_tree
        )
    minRadius: FloatProperty(
        name='Minimum Radius',
        description='Minimum branch Radius',
        min=0.0,
        default=0.0, update=update_tree
        )
    closeTip: BoolProperty(
        name='Close Tip',
        description='Set radius at branch tips to zero',
        default=False, update=update_tree
        )
    rootFlare: FloatProperty(
        name='Root Flare',
        description='Root radius factor',
        min=1.0,
        default=1.0, update=update_tree
        )
    autoTaper: BoolProperty(
        name='Auto Taper',
        description='Calculate taper automatically based on branch lengths',
        default=True, update=update_tree
        )
    taper: FloatVectorProperty(
        name='Taper',
        description='The fraction of tapering on each branch (nTaper)',
        min=0.0,
        max=1.0,
        default=[1, 1, 1, 1],
        size=4, update=update_tree
        )
    radiusTweak: FloatVectorProperty(
        name='Tweak Radius',
        description='multiply radius by this factor',
        min=0.0,
        max=1.0,
        default=[1, 1, 1, 1],
        size=4, update=update_tree
        )
    ratioPower: FloatProperty(
        name='Branch Radius Ratio',
        description=('Power which defines the radius of a branch compared to '
        'the radius of the branch it grew from (RatioPower)'),
        min=0.0,
        default=1.2, update=update_tree
        )
    downAngle: FloatVectorProperty(
        name='Down Angle',
        description=('The angle between a new branch and the one it grew '
        'from (nDownAngle)'),
        default=[90, 60, 45, 45],
        size=4, update=update_tree
        )
    downAngleV: FloatVectorProperty(
        name='Down Angle Variation',
        description="Angle to decrease Down Angle by towards end of parent branch "
                    "(negative values add random variation)",
        default=[0, -50, 10, 10],
        size=4, update=update_tree
        )
    useOldDownAngle: BoolProperty(
        name='Use old down angle variation',
        default=False, update=update_tree
        )
    useParentAngle: BoolProperty(
        name='Use parent angle',
        description='(first level) Rotate branch to match parent branch',
        default=True, update=update_tree
        )
    rotate: FloatVectorProperty(
        name='Rotate Angle',
        description="The angle of a new branch around the one it grew from "
                    "(negative values rotate opposite from the previous)",
        default=[137.5, 137.5, 137.5, 137.5],
        size=4, update=update_tree
        )
    rotateV: FloatVectorProperty(
        name='Rotate Angle Variation',
        description='Variation in the rotate angle (nRotateV)',
        default=[0, 0, 0, 0],
        size=4, update=update_tree
        )
    scale0: FloatProperty(
        name='Radius Scale',
        description='The scale of the trunk radius (0Scale)',
        min=0.0,
        default=1.0, update=update_tree
        )
    scaleV0: FloatProperty(
        name='Radius Scale Variation',
        description='Variation in the radius scale (0ScaleV)',
        min=0.0,
        max=1.0,
        default=0.2, update=update_tree
        )
    pruneWidth: FloatProperty(
        name='Prune Width',
        description='The width of the envelope (PruneWidth)',
        min=0.0,
        default=0.4, update=update_tree
        )
    pruneBase: FloatProperty(
        name='Prune Base Height',
        description='The height of the base of the envelope, bound by trunk height',
        min=0.0,
        max=1.0,
        default=0.3, update=update_tree
        )
    pruneWidthPeak: FloatProperty(
        name='Prune Width Peak',
        description=("Fraction of envelope height where the maximum width "
                     "occurs (PruneWidthPeak)"),
        min=0.0,
        default=0.6, update=update_tree
        )
    prunePowerHigh: FloatProperty(
        name='Prune Power High',
        description=('Power which determines the shape of the upper portion '
        'of the envelope (PrunePowerHigh)'),
        default=0.5, update=update_tree
        )
    prunePowerLow: FloatProperty(
        name='Prune Power Low',
        description=('Power which determines the shape of the lower portion '
        'of the envelope (PrunePowerLow)'),
        default=0.001, update=update_tree
        )
    pruneRatio: FloatProperty(
        name='Prune Ratio',
        description='Proportion of pruned length (PruneRatio)',
        min=0.0,
        max=1.0,
        default=1.0, update=update_tree
        )
    leaves: IntProperty(
        name='Leaves',
        description="Maximum number of leaves per branch (negative values grow "
                    "leaves from branch tip (palmate compound leaves))",
        min=3,
        # soft_min=20,
        # soft_max=20,
        max=50,
        default=15, update=update_tree
        )
    leafDownAngle: FloatProperty(
        name='Leaf Down Angle',
        description='The angle between a new leaf and the branch it grew from',
        default=45, update=update_leaves
        )
    leafDownAngleV: FloatProperty(
        name='Leaf Down Angle Variation',
        description="Angle to decrease Down Angle by towards end of parent branch "
                    "(negative values add random variation)",
        default=10, update=update_tree
        )
    leafRotate: FloatProperty(
        name='Leaf Rotate Angle',
        description="The angle of a new leaf around the one it grew from "
                    "(negative values rotate opposite from previous)",
        default=137.5, update=update_tree
        )
    leafRotateV: FloatProperty(
        name='Leaf Rotate Angle Variation',
        description='Variation in the rotate angle',
        default=0.0, update=update_leaves
        )
    leafScale: FloatProperty(
        name='Leaf Scale',
        description='The scaling applied to the whole leaf (LeafScale)',
        min=0.0,
        default=0.17, update=update_leaves
        )
    leafScaleX: FloatProperty(
        name='Leaf Scale X',
        description=('The scaling applied to the x direction of the leaf '
        '(LeafScaleX)'),
        min=0.0,
        default=1.0, update=update_leaves
        )
    leafScaleT: FloatProperty(
        name='Leaf Scale Taper',
        description='scale leaves toward the tip or base of the patent branch',
        min=-1.0,
        max=1.0,
        default=0.0, update=update_leaves
        )
    leafScaleV: FloatProperty(
        name='Leaf Scale Variation',
        description='randomize leaf scale',
        min=0.0,
        max=1.0,
        default=0.0, update=update_leaves
        )
    leafShape: EnumProperty(
        name='Leaf Shape',
        description='The shape of the leaves',
        items=(('hex', 'Hexagonal', 'hex'), ('rect', 'Rectangular', 'rect'), ('tri', 'Triangle', 'tri'),('dVert', 'Leaf Object', 'dVert')),
        default='rect', update=update_leaf_shape
        )
    leafDupliObj: EnumProperty(
        name='Leaf Object',
        description='Object to use for leaf instancing if Leaf Shape is DupliFaces or DupliVerts',
        items=objectList,
        update=update_leaves
        )

    leaf_flipUV: BoolProperty(
        name='leaf_flipUV',
        description='rotates uv set',
        default=False, update=update_tree
    )
    leaf_flipUVrandom: BoolProperty(
        name='leaf_flipUVrandom',
        description='rotates uv set',
        default=False, update=update_tree
    )
    leaf_UVSize: FloatVectorProperty(
        name='leaf_UVSize',
        description='UV Coordinate Size',
        min=0.0,
        max=100.0,
        default=[1, 1],
        size=2, update=update_tree
        )

    bend: FloatProperty(
        name='Leaf Bend',
        description='The proportion of bending applied to the leaf (Bend)',
        min=0.0,
        max=5.0,
        default=0.0, update=update_leaves
        )

    leafangle: FloatProperty(
        name='Leaf Angle',
        description='Leaf vertical attraction',
        default=0.0, update=update_leaves
        )
    horzLeaves: BoolProperty(
        name='Horizontal leaves',
        description='Leaves face upwards',
        default=True, update=update_leaves
        )
    leafDist: EnumProperty(
        name='Leaf Distribution',
        description='The way leaves are distributed on branches',
        items=shapeList4,
        default='6', update=update_tree
        )
    bevelRes: IntProperty(
        name='Bevel Resolution',
        description='The bevel resolution of the curves',
        min=0,
        max=16,
        default=0, update=update_tree
        )
    resU: IntProperty(
        name='Curve Resolution',
        description='The resolution along the curves',
        min=1,
        max=10,
        default=4, update=update_tree
        )
    handleType: EnumProperty(
        name='Handle Type',
        description='The type of handles used in the spline',
        items=handleList,
        default='0', update=update_tree
        )
    armAnim: BoolProperty(
        name='Armature Animation',
        description='Whether animation is added to the armature',
        default=False, update=update_tree
        )
    previewArm: BoolProperty(
        name='Fast Preview',
        description='Disable armature modifier, hide tree, and set bone display to wire, for fast playback',
        # Disable skin modifier and hide tree and armature, for fast playback
        default=False, update=update_tree
        )
    leafAnim: BoolProperty(
        name='Leaf Animation',
        description='Whether animation is added to the leaves',
        default=False, update=update_tree
        )
    frameRate: FloatProperty(
        name='Animation Speed',
        description=('Adjust speed of animation, relative to scene frame rate'),
        min=0.001,
        default=1, update=update_tree
        )
    loopFrames: IntProperty(
        name='Loop Frames',
        description='Number of frames to make the animation loop for, zero is disabled',
        min=0,
        default=0, update=update_tree
        )
    windSpeed: FloatProperty(
        name='Wind Speed',
        description='The wind speed to apply to the armature',
        default=2.0, update=update_tree
        )
    windGust: FloatProperty(
        name='Wind Gust',
        description='The greatest increase over Wind Speed',
        default=0.0, update=update_tree
        )
    wind: FloatProperty(
        name='Overall Wind Strength',
        description='The intensity of the wind to apply to the armature',
        default=1.0, update=update_tree
        )
    gust: FloatProperty(
        name='Wind Gust Strength',
        description='The amount of directional movement, (from the positive Y direction)',
        default=1.0, update=update_tree
        )
    gustF: FloatProperty(
        name='Wind Gust Fequency',
        description='The Frequency of directional movement',
        default=0.075, update=update_tree
        )
    af1: FloatProperty(
        name='Amplitude',
        description='Multiplier for noise amplitude',
        default=1.0, update=update_tree
        )
    af2: FloatProperty(
        name='Frequency',
        description='Multiplier for noise fequency',
        default=1.0, update=update_tree
        )
    af3: FloatProperty(
        name='Randomness',
        description='Random offset in noise',
        default=4.0, update=update_tree
        )
    makeMesh: BoolProperty(
        name='Make Mesh',
        description='Convert curves to mesh, uses skin modifier, enables armature simplification',
        default=False, update=update_tree
        )
    convertToMesh: BoolProperty(
        name='Convert to Mesh',
        description='Convert curves to mesh, uses convert funktion',
        default=True, update=update_tree
        )
    armLevels: IntProperty(
        name='Armature Levels',
        description='Number of branching levels to make bones for, 0 is all levels',
        min=0,
        default=2, update=update_tree
        )
    boneStep: IntVectorProperty(
        name='Bone Length',
        description='Number of stem segments per bone',
        min=1,
        default=[1, 1, 1, 1],
        size=4, update=update_tree
        )
    presetName: StringProperty(
        name='Preset Name',
        description='The name of the preset to be saved',
        default='',
        subtype='FILE_NAME', update=no_update_tree
        )
    limitImport: BoolProperty(
        name='Limit Import',
        description='Limited imported tree to 2 levels & no leaves for speed',
        default=True, update=no_update_tree
        )
    overwrite: BoolProperty(
        name='Overwrite',
        description='When checked, overwrite existing preset files when saving',
        default=False, update=no_update_tree
        )
    """
    startCurv: FloatProperty(
        name='Trunk Starting Angle',
        description=('The angle between vertical and the starting direction'
        'of the trunk'),
        min=0.0,
        max=360,
        default=0.0, update=update_tree
        )
    """

    def get_property_dict(self):
        print("outside of loop")
        blacklist = ["chooseSet", "presetName", "limitImport", "do_update", "overwrite", "leafDupliObj", "istree"]

        data = []
        for a, b in (self.items()):
            # print("in property diect loop")
            if a in blacklist:
                continue
            # If the property is a vector property then add the slice to the list
            try:
                len(b)
                data.append((a, b[:]))
            # Otherwise, it is fine so just add it
            except:
                data.append((a, b))
        # Create the dict from the list
        data = dict(data)
        #set enums
        data["leafShape"] = self.leafShape
        data["rMode"] = self.rMode
        data["shape"] = self.shape
        data["shapeS"] = self.shapeS
        data["leafDist"] = self.leafDist
        data["handleType"] = self.handleType
        return data


    def draw(self, layout):
        # layout = self.layout

        # Branch specs
        # layout.label('Tree Definition')

        layout.prop(self, 'chooseSet')

        if self.chooseSet == '0':
            box = layout.box()
            box.label(text="Geometry:")
            box.prop(self, 'bevel')
            box.prop(self, 'convertToMesh')

            row = box.row()
            row.prop(self, 'bevelRes')
            row.prop(self, 'resU')

            box.prop(self, 'handleType')
            box.prop(self, 'shape')
            if self.shape == '8':
                col = box.column()
                col.prop(self, 'customShape')

            row = box.row()
            box.prop(self, 'shapeS')
            box.prop(self, 'branchDist')
            box.prop(self, 'nrings')
            box.prop(self, 'seed')

            box.label(text="Tree Scale:")
            row = box.row()
            row.prop(self, 'scale')
            row.prop(self, 'scaleV')

            box.label(text="UV Properties:")
            row =box.row()
            row.prop(self, 'rotateUV')
            row.prop(self, 'UVSize')


            box.label(text="Presets:")
            row = box.row()
            row.prop(self, 'overwrite')
            row.prop(self, 'limitImport')

            row = box.row()
            row.prop(self, 'presetName')
            # Send the data dict and the file name to the exporter
            row.operator('baumschule.exportdata').data = repr([self.presetName, self.overwrite])
            box.label(text="Load Preset:")
            row = box.row()
            row.menu('BAUMSCHULE_MT_preset', text='Load Preset')

        elif self.chooseSet == '1':
            box = layout.box()
            box.label(text="Branch Radius:")

            row = box.row()
            row.prop(self, 'bevel')
            row.prop(self, 'bevelRes')

            box.prop(self, 'ratio')
            row = box.row()
            row.prop(self, 'scale0')
            row.prop(self, 'scaleV0')
            box.prop(self, 'ratioPower')

            box.prop(self, 'minRadius')
            box.prop(self, 'closeTip')
            box.prop(self, 'rootFlare')

            box.prop(self, 'autoTaper')

            split = box.split()
            col = split.column()
            col.prop(self, 'taper')
            col = split.column()
            col.prop(self, 'radiusTweak')

        elif self.chooseSet == '2':
            box = layout.box()
            box.label(text="Branch Splitting:")
            box.prop(self, 'levels')
            box.prop(self, 'baseSplits')
            row = box.row()
            row.prop(self, 'baseSize')
            row.prop(self, 'baseSize_s')
            box.prop(self, 'splitHeight')
            box.prop(self, 'splitBias')
            box.prop(self, 'splitByLen')

            split = box.split()

            col = split.column()
            col.prop(self, 'branches')
            col.prop(self, 'splitAngle')
            col.prop(self, 'rotate')
            col.prop(self, 'attractOut')

            col = split.column()
            col.prop(self, 'segSplits')
            col.prop(self, 'splitAngleV')
            col.prop(self, 'rotateV')

            col.label(text="Branching Mode:")
            col.prop(self, 'rMode')

            box.column().prop(self, 'curveRes')
            # box.column().prop(self, 'deadBranch_C')


        elif self.chooseSet == '3':
            box = layout.box()
            box.label(text="Branch Growth:")

            box.prop(self, 'taperCrown')

            split = box.split()

            col = split.column()
            col.prop(self, 'length')
            col.prop(self, 'downAngle')
            col.prop(self, 'curve')
            col.prop(self, 'curveBack')

            col = split.column()
            col.prop(self, 'lengthV')
            col.prop(self, 'downAngleV')
            col.prop(self, 'curveV')
            col.prop(self, 'attractUp')

            box.prop(self, 'useOldDownAngle')
            box.prop(self, 'useParentAngle')


        elif self.chooseSet == '4':
            box = layout.box()
            box.enabled = self.convertToMesh
            text = "Leaves:" + "" if self.convertToMesh else "(Convert to Mesh needs to be enabled!)"
            box.label(text=text)
            box.prop(self, 'showLeaves')
            box = box.column()
            box.enabled = self.showLeaves
            box.prop(self, 'leafShape')
            row = box.row()
            row.enabled= self.leafShape == 'dVert'
            #  ('dVert', 'DupliVerts', 'dVert')
            box = box.column()
            if row.enabled and self.leafDupliObj:
                if self.leafDupliObj == 'NONE':
                    row.label(text="No appropriate objects in the Scene", icon='ERROR')
                    box.enabled = False
                else:
                    box.enabled = True
                    row.prop(self, 'leafDupliObj')
            box.prop(self, 'leaves')
            box.prop(self, 'leafDist')

            box.label(text="")
            row = box.row()
            row.prop(self, 'leafDownAngle')
            row.prop(self, 'leafDownAngleV')

            row = box.row()
            row.prop(self, 'leafRotate')
            row.prop(self, 'leafRotateV')
            box.label(text="")

            row = box.row()
            row.prop(self, 'leafScale')
            row.prop(self, 'leafScaleX')

            row = box.row()
            row.prop(self, 'leafScaleT')
            row.prop(self, 'leafScaleV')

            box.prop(self, 'horzLeaves')
            box.prop(self, 'leafangle')

            box.label(text="UV Properties:")
            row =box.row()
            row.prop(self, 'leaf_flipUV', text='Flip UV Coords')
            row.prop(self, 'leaf_flipUVrandom', text='random flipping')
            row.prop(self, 'leaf_UVSize', text='UV Size')
            row =box.row()
            # box.label(" ")
            # box.prop(self, 'bend')
        elif self.chooseSet == '5':
            box = layout.box()
            box.label(text="Prune:")
            box.prop(self, 'prune')
            box.prop(self, 'pruneRatio')
            row = box.row()
            row.prop(self, 'pruneWidth')
            row.prop(self, 'pruneBase')
            box.prop(self, 'pruneWidthPeak')

            row = box.row()
            row.prop(self, 'prunePowerHigh')
            row.prop(self, 'prunePowerLow')

        elif self.chooseSet == '6':
            box = layout.box()
            box.label(text="Armature:")
            row = box.row()
            row.prop(self, 'useArm')
            # box.prop(self, 'makeMesh')
            box.label(text="Armature Simplification:")
            box.prop(self, 'armLevels')
            box.prop(self, 'boneStep')

        elif self.chooseSet == '7':
            box = layout.box()
            box.label(text="Finalize All Other Settings First!")
            box.prop(self, 'armAnim')
            box.prop(self, 'leafAnim')
            box.prop(self, 'previewArm')
            box.prop(self, 'frameRate')
            box.prop(self, 'loopFrames')

            # row = box.row()
            # row.prop(self, 'windSpeed')
            # row.prop(self, 'windGust')

            box.label(text='Wind Settings:')
            box.prop(self, 'wind')
            row = box.row()
            row.prop(self, 'gust')
            row.prop(self, 'gustF')

            box.label(text='Leaf Wind Settings:')
            box.prop(self, 'af1')
            box.prop(self, 'af2')
            box.prop(self, 'af3')

def menu_func(self, context):
    self.layout.operator(NewTree.bl_idname, text="Baumschule", icon_value=custom_icons["custom_icon"].icon_id)



def getScriptDir():
    for p in bpy.utils.script_paths():
        sp = os.path.join(p, 'addons', 'baumschule')
        if os.path.exists(sp):
            return sp

classes = (
    AddTree,
    PresetMenu,
    ImportData,
    ExportData,
    NewTree,
    tree_tree_props,
)

def register():
    global custom_icons
    custom_icons = bpy.utils.previews.new()
    custom_icons.load("custom_icon", os.path.join(getScriptDir(), "icons", "icon_baum.png"), 'IMAGE')
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Object.tree_props = bpy.props.PointerProperty(type=tree_tree_props)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    global custom_icons
    bpy.utils.previews.remove(custom_icons)
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)


if __name__ == "__main__":
    register()
