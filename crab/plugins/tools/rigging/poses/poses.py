import crab
from crab.vendor import qute
import pymel.core as pm
import json


# --------------------------------------------------------------------------------------
class DefineAPoseTool(crab.RigTool):
    identifier = "poses_define_a_pose"
    display_name = "Define A Pose"
    icon = "poses.png"
    tooltips = dict(
        selection_only="If true, only the selected objects will be affected",
    )
    POSE_NAME = "APose"

    # ----------------------------------------------------------------------------------
    def __init__(self):
        super(DefineAPoseTool, self).__init__()
        self.options.selection_only = False

    # ----------------------------------------------------------------------------------
    def run(self):

        selection_state_text = "all joints"

        confirm_result = "Yes"
        if self.options.selection_only:
            nodes = pm.selected()
            selection_state_text = "selected joints"

        else:
            confirm_result = pm.confirmDialog(
                title="Confirm",
                message=f"This will replace the entire {self.POSE_NAME}, Are you sure?",
                button=["Yes", "No"],
                defaultButton="Yes",
                cancelButton="No",
                dismissString="No"
            )
            nodes = pm.ls("%s_*" % crab.config.SKELETON, type="joint", r=True)
            nodes.extend(pm.ls("%s_*" % crab.config.GUIDE, type="transform", r=True))

        if confirm_result == "Yes":
            with crab.utils.contexts.UndoChunk():
                for joint in nodes:
                    if not joint.hasAttr(self.POSE_NAME):
                        joint.addAttr(self.POSE_NAME, at="matrix")
                    joint.attr(self.POSE_NAME).set(joint.getMatrix())
            pm.displayInfo(
                "Updated: {} on {}".format(
                    self.POSE_NAME,
                    selection_state_text,
                ),
            )

        else:
            pm.displayInfo("Action Cancelled: {}".format(self.POSE_NAME))


# --------------------------------------------------------------------------------------
class ApplyAPoseTool(crab.RigTool):
    identifier = "poses_apply_a_pose"
    display_name = "Apply A Pose"
    icon = "poses.png"
    tooltips = dict(
        selection_only="If true, only the selected objects will be affected",
        rotate_only="If True only the rotation will be applied",
    )

    POSE_NAME = "APose"

    # ----------------------------------------------------------------------------------
    def __init__(self):
        super(ApplyAPoseTool, self).__init__()
        self.options.selection_only = False
        self.options.rotate_only = False
        self.options.translate_only = False

    # ----------------------------------------------------------------------------------
    def run(self):

        # -- Ensure all rigs are editable
        for rig in crab.Rig.all():
            if not rig.is_editable():

                confirmation = qute.utilities.request.confirmation(
                    title="%s is not editable" % rig.node().name(),
                    label=(
                        "To assign a pose, the rig needs to be editable. Would you "
                        "like to put the rig into an editable state?"
                    ),
                )

                if confirmation:
                    rig.edit()

                else:

                    # -- If any rig is not intended to be editable, exit
                    return

        selection_state_text = "all joints"
        rotation_only_text = ""
        if self.options.selection_only:
            nodes = pm.selected()
            selection_state_text = "selected joints"

        else:
            nodes = pm.ls("%s_*" % crab.config.SKELETON, type="joint", r=True)
            nodes.extend(pm.ls("%s_*" % crab.config.GUIDE, type="transform", r=True))

        with crab.utils.contexts.UndoChunk():
            for joint in nodes:
                if joint.hasAttr(self.POSE_NAME):

                    pos = None
                    if self.options.rotate_only:
                        pos = joint.getTranslation()
                        rotation_only_text = "rotation only"

                    rot = None
                    if self.options.translate_only:
                        rot = joint.getRotation()
                        rotation_only_text = "translation only"

                    joint.setMatrix(joint.attr(self.POSE_NAME).get())

                    if pos:
                        joint.setTranslation(pos)

                    if rot:
                        joint.setRotation(rot)

        pm.displayInfo("Loaded: {} to {} {}".format(
            self.POSE_NAME,
            selection_state_text,
            rotation_only_text
        ))


# --------------------------------------------------------------------------------------
class DefineTPoseTool(DefineAPoseTool):
    identifier = "poses_define_t_pose"
    display_name = "Define T Pose"
    category = "Poses"
    POSE_NAME = "TPose"


# --------------------------------------------------------------------------------------
class ApplyTPoseTool(ApplyAPoseTool):
    identifier = "poses_apply_t_pose"
    display_name = "Apply T Pose"
    POSE_NAME = "TPose"


# --------------------------------------------------------------------------------------
class StoreATPoses(crab.RigTool):
    """
    This will Store all the A and T Pose data of all skeletal joints
    """

    identifier = "write_a_and_t_pose"
    display_name = "Save A and T Poses to file"

    # ----------------------------------------------------------------------------------
    def __init__(self):
        super(StoreATPoses, self).__init__()

    # ----------------------------------------------------------------------------------
    def run(self, save_path=None):

        if not save_path:
            save_path = qute.utilities.request.filepath(
                "Select Location to Save",
                save=True,
            )

            if not save_path.lower().endswith(".json"):
                save_path = save_path + ".json"

        if not save_path:
            return

        data_to_save = dict()

        for joint in pm.ls("SKL_*", type="joint"):

            a_matrix = list()
            t_matrix = list()

            if joint.hasAttr("APose"):

                for part in joint.attr("APose").get():
                    a_matrix.extend(part)

            if joint.hasAttr("TPose"):
                for part in joint.attr("TPose").get():
                    t_matrix.extend(part)

            attr_data = dict(
                APose=a_matrix,
                TPose=t_matrix,
            )
            data_to_save[joint.name()] = attr_data

        with open(save_path, "w") as f:
            json.dump(
                data_to_save,
                f,
                sort_keys=True,
                indent=4,
            )


# --------------------------------------------------------------------------------------
class ReadATPoses(crab.RigTool):
    """
    This will Store all the A and T Pose data of all skeletal joints
    """

    identifier = "read_a_and_t_pose"
    display_name = "Read A and T Poses from file"

    # ----------------------------------------------------------------------------------
    def __init__(self):
        super(ReadATPoses, self).__init__()

    # ----------------------------------------------------------------------------------
    def run(self, file_path=None):

        if not file_path:
            file_path = qute.utilities.request.filepath(
                "Select Pose file to load",
                save=False,
            )

        if not file_path:
            return

        with open(file_path, "r") as f:
            data = json.load(f)

            for bone_name, poses in data.iteritems():

                if not pm.objExists(bone_name):
                    print("{} does not exist. Skipping.".format(bone_name))
                    continue

                bone = pm.PyNode(bone_name)

                if poses["APose"] and bone.hasAttr("APose"):
                    bone.APose.set(pm.dt.Matrix(poses["APose"]))

                if poses["TPose"] and bone.hasAttr("TPose"):
                    bone.TPose.set(pm.dt.Matrix(poses["TPose"]))

        return True
