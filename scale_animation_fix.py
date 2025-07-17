bl_info = {
    "name": "Scale Animation Fix",
    "author": "ingenoire",
    "version": (1, 0, 3),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Scale Animation",
    "description": "Adjusts Root bone translation and hips bone Y-axis movement for scaled animations.",
    "category": "Animation",
}

import bpy

# Add a property for scale factor
bpy.types.Scene.scale_factor = bpy.props.FloatProperty(
    name="Scale Factor",
    description="Scale factor for animation adjustments",
    default=1.0,
    min=0.1,
    max=100.0
)

# Operator to fix animation for scaled models
class FixAnimationForScaledModelsOperator(bpy.types.Operator):
    bl_idname = "object.fix_animation_scaled_models"
    bl_label = "Fix Animation for Scaled Models"
    bl_description = "Adjusts Root bone translation and hips bone Y-axis movement based on the scale factor for the '_base_' armature."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Find the '_base_' armature
        armature = None
        for obj in bpy.context.scene.objects:
            if obj.type == 'ARMATURE' and obj.name == "_base_":
                armature = obj
                break

        if not armature:
            self.report({'ERROR'}, "No armature named '_base_' found.")
            return {'CANCELLED'}

        scale_factor = context.scene.scale_factor
        anim_data = armature.animation_data

        if anim_data is None or anim_data.action is None:
            self.report({'ERROR'}, "No animation data found.")
            return {'CANCELLED'}

        action = anim_data.action
        root_bone_name = "Root"
        hips_bone_name = "hips"

        # Ensure we're in Pose Mode
        if bpy.context.mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')

        # Process Root bone translation (Y-axis)
        if root_bone_name in armature.pose.bones:
            root_bone = armature.pose.bones[root_bone_name]
            fcurve_loc_y = anim_data.action.fcurves.find(data_path=f"pose.bones[\"{root_bone_name}\"].location", index=1)
            
            for frame in range(int(action.frame_range[0]), int(action.frame_range[1]) + 1):
                bpy.context.scene.frame_set(frame)
                
                # Apply scale factor to Y-axis translation if keyframe exists
                if fcurve_loc_y and any(kp.co[0] == frame for kp in fcurve_loc_y.keyframe_points):
                    root_bone.location.y += scale_factor  # Translate by scale factor meters on Y-axis
                    root_bone.keyframe_insert(data_path="location", index=1, frame=frame)

        # Process hips bone Y-axis keyframes directly
        if hips_bone_name in armature.pose.bones:
            hips_bone = armature.pose.bones[hips_bone_name]
            fcurve_loc_y = anim_data.action.fcurves.find(data_path=f"pose.bones[\"{hips_bone_name}\"].location", index=1)
            
            if fcurve_loc_y:
                for keyframe in fcurve_loc_y.keyframe_points:
                    keyframe.co[1] *= scale_factor  # Multiply Y-axis value by scale factor
                    # Update the bone's pose to reflect the new keyframe value
                    bpy.context.scene.frame_set(int(keyframe.co[0]))
                    hips_bone.location.y = keyframe.co[1]
                    hips_bone.keyframe_insert(data_path="location", index=1, frame=keyframe.co[0])

        self.report({'INFO'}, f"Animation adjusted for scale factor {scale_factor} on '_base_' armature.")
        return {'FINISHED'}

# UI Panel
class ScaleAnimationPanel(bpy.types.Panel):
    bl_label = "Scale Animation Fix"
    bl_idname = "OBJECT_PT_scale_animation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Scale Animation'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Scale Animation", icon='MOD_ARMATURE')
        layout.prop(context.scene, 'scale_factor', text="Scale Factor")
        layout.operator("object.fix_animation_scaled_models", text="Fix Animation for Scale", icon='MODIFIER')

# Register/Unregister Functions
def register():
    bpy.utils.register_class(FixAnimationForScaledModelsOperator)
    bpy.utils.register_class(ScaleAnimationPanel)
    bpy.types.Scene.scale_factor = bpy.props.FloatProperty(
        name="Scale Factor",
        description="Scale factor for animation adjustments",
        default=1.0,
        min=0.1,
        max=100.0
    )

def unregister():
    bpy.utils.unregister_class(FixAnimationForScaledModelsOperator)
    bpy.utils.unregister_class(ScaleAnimationPanel)
    del bpy.types.Scene.scale_factor

if __name__ == "__main__":
    register()