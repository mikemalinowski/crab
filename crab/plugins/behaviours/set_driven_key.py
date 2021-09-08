import crab
from crab.vendor import qute

import pymel.core as pm


# ------------------------------------------------------------------------------
class SetDrivenKeyBehaviour(crab.Behaviour):
    """
    This behaviour allows you to generate a set driven key. For this to work you should
    first manually create your set driven key up as you want it, then apply this behaviour.

    Once applied, select your set driven key node (easist way is in through the attribute editor
    or the node editor) and then press the 'Copy' button in the 'Applied Behaviours' tab of
    crab.

    This will snapshot your set driven key and it will be re-created each time the rig
    is rebuilt.
    """
    identifier = 'Set Driven Key'

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(SetDrivenKeyBehaviour, self).__init__(*args, **kwargs)

        self.options.curve_data = ''

    # --------------------------------------------------------------------------
    def apply(self):

        if not self.options.curve_data:
            # -- Blank data means it has not yet been set/defined
            return True

        # -- Attempt to load the data
        try:
            curve_data = eval(self.options.curve_data)

        except:
            raise Exception('Could not load curve data : %s' % self.options.curve_data)

        # -- Perform the deserialisation
        self.deserialise(curve_data)

        return True

    # --------------------------------------------------------------------------
    def ui(self, parent=None):
        return SetDrivenKeyUI

    # --------------------------------------------------------------------------
    def serialise(self, node=None):

        # -- If we're not given a specific node, then look at the selection
        try:
            node = node or pm.selected()[0]

        except:
            print('No set driven key provided.')
            return False

        # -- Check our node is valid
        if 'animCurveU' not in node.nodeType():
            print('%s is not of type AnimCurveU*' % node)
            return False

        curve_data = dict(
            driver=node.attr('input').inputs(plugs=True)[0].name(),
            driven=node.attr('output').outputs(plugs=True)[0].name(),
            node_type=node.nodeType(),
            post_infinity_type=node.getPostInfinityType().index,
            pre_infinity_type=node.getPreInfinityType().index,
            key_data=list(),
        )
        in_tangents_x = pm.keyTangent(node, q=True, ix=True)
        in_tangents_y = pm.keyTangent(node, q=True, iy=True)

        out_tangents_x = pm.keyTangent(node, q=True, ox=True)
        out_tangents_y = pm.keyTangent(node, q=True, oy=True)

        for key_idx in range(node.numKeys()):
            time = node.getUnitlessInput(key_idx)

            key_data = dict(
                time=time,
                value=node.getValue(key_idx),
                in_tangent_type=node.getInTangentType(key_idx).index,
                out_tangent_type=node.getOutTangentType(key_idx).index,
                locked_tangent=node.getTangentsLocked(key_idx),
                locked_weights=node.getWeightsLocked(key_idx),
                is_breakdown=node.isBreakdown(key_idx),
                in_tangent=[in_tangents_x[key_idx], in_tangents_y[key_idx]],
                out_tangent=[out_tangents_x[key_idx], out_tangents_y[key_idx]],
            )

            curve_data['key_data'].append(key_data)

        self.options.curve_data = str(curve_data)
        self.save()

        return curve_data

    # --------------------------------------------------------------------------
    def deserialise(self, data):

        # -- Start by creating the node
        node = pm.createNode(data['node_type'])
        pm.PyNode(data['driver']).connect(node.attr('input'), force=True)
        node.attr('output').connect(data['driven'], force=True)

        # -- Set the curve data
        node.preInfinity.set(data['pre_infinity_type'])
        node.postInfinity.set(data['post_infinity_type'])

        # -- Now build the curve
        for key_data in data['key_data']:
            pm.setDrivenKeyframe(
                data['driven'],
                currentDriver=data['driver'],
                driverValue=key_data['time'],
                value=key_data['value'],
            )

            # -- Get the key index
            key_idx = node.numKeys() - 1

            # -- Set the key properties
            node.setInTangentType(key_idx, key_data['in_tangent_type'])
            node.setOutTangentType(key_idx, key_data['out_tangent_type'])

            pm.keyTangent(
                index=[key_idx, key_idx],
                ix=key_data['in_tangent'][0],
                iy=key_data['in_tangent'][1],
                ox=key_data['out_tangent'][0],
                oy=key_data['out_tangent'][1],
            )


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
class SetDrivenKeyUI(crab.BehaviourUI):

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(SetDrivenKeyUI, self).__init__(*args, **kwargs)

        # -- Create a default layout
        self.setLayout(qute.QVBoxLayout())

        # -- Add a button to copy the currently selected
        # -- set driven key node - this will instigate a
        # -- serialisation of the data
        self.serialiseButton = qute.QPushButton('Copy')
        self.layout().addWidget(self.serialiseButton)

        # -- Hook up the signals and slots
        self.serialiseButton.clicked.connect(self.serialise)

    # --------------------------------------------------------------------------
    def serialise(self):

        result = None
        try:
            result = self.behaviour_instance.serialise()

        except:
            pass

        finally:
            if not result:
                qute.utilities.request.message(
                    title='Could not copy',
                    label='Something went wrong when recording the Set Driven Key. See the script editor for details. \n\nNote - you MUST select an AnimCurveU* node'
                )
                return False

        qute.utilities.request.message(
            title='Set Driven Key Recorded',
            label='The set driven can has been successfully recorded',
            parent=self,
        )
        return True

    @classmethod
    def unhandled_options(cls):
        return ['description']
