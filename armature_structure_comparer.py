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
    "name": "Armature Structure Comparer",
    "author": "todashuta",
    "version": (1, 0, 3),
    "blender": (2, 80, 0),
    "location": "3D View > Side Bar > Armature > Armature Structure Comparer",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "https://github.com/todashuta/blender-addon-armature-structure-comparer",
    "category": "Rigging"
}


import bpy


class ARMATURE_STRUCTURE_COMPARER_PT_panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Armature"
    bl_label = "Armature Structure Comparer"

    @classmethod
    def poll(self, context):
        active_object = context.active_object
        return active_object and active_object.mode == "OBJECT"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.prop(scene, "armature_structure_comparer_armatureA")
        layout.prop(scene, "armature_structure_comparer_armatureB")

        armatureA = scene.armature_structure_comparer_armatureA
        armatureB = scene.armature_structure_comparer_armatureB

        layout.separator()

        if armatureA is None:
            layout.label(icon="INFO", text="Please Set Armature A Object")
            return
        if armatureB is None:
            layout.label(icon="INFO", text="Please Set Armature B Object")
            return

        armatureA_bonenames = set(armatureA.data.bones.keys())
        armatureB_bonenames = set(armatureB.data.bones.keys())

        existsOnlyInA = armatureA_bonenames - armatureB_bonenames
        existsOnlyInB = armatureB_bonenames - armatureA_bonenames
        existsInBoth  = armatureB_bonenames & armatureA_bonenames

        layout.label(text="Exists only in A:")
        for name in existsOnlyInA:
            layout.label(icon="BONE_DATA", text=name)

        layout.label(text="Exists only in B:")
        for name in existsOnlyInB:
            layout.label(icon="BONE_DATA", text=name)

        layout.label(text="Parent Bone not Matched:")
        for name in existsInBoth:
            a_parent = armatureA.data.bones[name].parent
            b_parent = armatureB.data.bones[name].parent
            parent_type_mismatch = type(a_parent) is not type(b_parent)
            parent_name_mismatch = a_parent is not None and b_parent is not None and a_parent.name != b_parent.name

            if parent_type_mismatch or parent_name_mismatch:
                layout.label(icon="BONE_DATA", text=name)


panels = (
        ARMATURE_STRUCTURE_COMPARER_PT_panel,
)


def update_panel(self, context):
    message = "Armature Structure Comparer: Updating Panel locations has failed"
    try:
        for panel in panels:
            if "bl_rna" in panel.__dict__:
                bpy.utils.unregister_class(panel)

        for panel in panels:
            panel.bl_category = context.preferences.addons[__name__].preferences.category
            bpy.utils.register_class(panel)

    except Exception as e:
        print("\n[{}]\n{}\n\nError:\n{}".format(__name__, message, e))
        pass


class ARMATURE_STRUCTURE_COMPARER_Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    category: bpy.props.StringProperty(name="Side Bar Tab Category", default="Armature", update=update_panel)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "category")


classes = (
        ARMATURE_STRUCTURE_COMPARER_PT_panel,
        ARMATURE_STRUCTURE_COMPARER_Preferences,
)


def armature_poll_func(self, object) -> bool:
    return object.type == "ARMATURE"


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.armature_structure_comparer_armatureA = bpy.props.PointerProperty(
                name="Armature A", type=bpy.types.Object, poll=armature_poll_func)
    bpy.types.Scene.armature_structure_comparer_armatureB = bpy.props.PointerProperty(
                name="Armature B", type=bpy.types.Object, poll=armature_poll_func)
    update_panel(None, bpy.context)


def unregister():
    if hasattr(bpy.types.Scene, "armature_structure_comparer_armatureA"):
        del bpy.types.Scene.armature_structure_comparer_armatureA
    if hasattr(bpy.types.Scene, "armature_structure_comparer_armatureB"):
        del bpy.types.Scene.armature_structure_comparer_armatureB

    for c in reversed(classes):
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
