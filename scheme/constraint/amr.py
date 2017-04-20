from util.amr import *


class Constraints(constraints.Constraints):
    def __init__(self, args):
        super(Constraints, self).__init__(args, require_connected=True,
                                          require_implicit_childless=False, allow_root_terminal_children=True,
                                          possible_multiple_incoming=TERMINAL_TAGS, unique_outgoing=(),
                                          childless_incoming_trigger=(), unique_incoming=(),
                                          mutually_exclusive_outgoing=(), top_level=None)
        self.tag_rules.append(
            constraints.TagRule(trigger={constraints.Direction.incoming: "name"},
                                allowed={constraints.Direction.outgoing: re.compile(
                                    "^(%s|op\d+)$" % "|".join(TERMINAL_TAGS))}))

    def allow_action(self, action, history):
        return True

    def _allow_edge(self, edge):
        return edge not in edge.parent.outgoing  # Prevent multiple identical edges between the same pair of nodes

    def allow_parent(self, node, tag):
        return (not node.implicit or tag not in TERMINAL_TAGS) and \
               (is_concept(node.label) or tag in TERMINAL_TAGS) and \
               is_valid_arg(node, node.label, tag)

    def allow_child(self, node, tag):
        return (node.label == MINUS or tag != POLARITY) and \
               is_valid_arg(node, node.label, tag, is_parent=False)

    def allow_label(self, node, label):
        return (is_concept(label) or node.outgoing_tags <= TERMINAL_TAGS) and \
               (label != MINUS or node.incoming_tags <= {POLARITY}) and \
               (not node.parents or
                is_valid_arg(node, label, *node.outgoing_tags) and
                is_valid_arg(node, label, *node.incoming_tags, is_parent=False))
