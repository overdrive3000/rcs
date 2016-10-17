#!/usr/bin/env python

import subprocess
import math
import json
import i3ipc

i3 = i3ipc.Connection()

get_workspaces_cmd = 'i3-msg -t get_workspaces'.split()
get_outputs_cmd = 'i3-msg -t get_outputs'.split()


def get_workspaces():
    return json.loads(subprocess.check_output(get_workspaces_cmd))


def get_outputs():

    def active(output):
        return output['active'] == True

    return filter(active, json.loads(subprocess.check_output(get_outputs_cmd)))


def get_names(things):
    return [t['name'] for t in things]


def get_focused_workspace(workspaces):
    return filter(lambda workspace: workspace['focused'], workspaces)


def workspaces_sorted_by_number(workspaces):
    return sorted(workspaces, key=lambda workspace: int(workspace['num']))


def outputs_from_left_to_right(outputs):
    return sorted(outputs, key=lambda output: output['rect']['x'])


def go_to_workspace(workspace):
    if workspace:
        go_to_workspace_cmd = ['i3-msg', 'workspace', workspace]
        subprocess.call(go_to_workspace_cmd)


def move_workspace(workspace, output):
    move_workspace_cmd = [
            'i3-msg', 'move', 'workspace', 'to', 'output', output
            ]
    go_to_workspace(workspace)
    subprocess.call(move_workspace_cmd)


def _reflow(workspaces, outputs):
    """
        workspaces is a list of workspace names i.e. ['1', '2', '3']
        outputs is a list of output names i.e. ['VGA1', 'DP1']
    """
    i = 0
    j = 1
    workspaces_per_output = math.ceil(float(len(workspaces)) / len(outputs))
    while j < len(workspaces) + 1:
        workspace = workspaces[j - 1]
        output = outputs[i]
        print workspace, ' goes on ', output
        move_workspace(workspace, output)
        if math.fmod(j, workspaces_per_output) == 0 and i < len(outputs) - 1:
            i += 1
        j += 1


def get_non_empty_workspaces():
    tree = i3.get_tree()

    outputs = [o for o in tree.nodes if o.name != '__i3']
    non_empty_workspaces = []
    empty_workspaces = []
    for output in outputs:
        for con in [c for c in output.nodes if c.type == 'con']:
            for workspace in [w for w in con.nodes if w.type == 'workspace']:
                if len(workspace.nodes) > 0:
                    non_empty_workspaces.append(workspace.name)
                else:
                    empty_workspaces.append(workspace.name)

    return non_empty_workspaces


def reflow_from_left_to_right():
    workspaces = get_workspaces()
    outputs = get_outputs()
    non_empty_workspaces = get_non_empty_workspaces()

    focused_workspaces = get_names(get_focused_workspace(workspaces))
    focused_workspace = focused_workspaces[0] if focused_workspaces else None

    workspace_names = filter(lambda w: w in non_empty_workspaces, get_names(workspaces_sorted_by_number(workspaces)))
    output_names = get_names(outputs_from_left_to_right(outputs))

    print 'workspaces found: ',  workspace_names
    print 'outputs found: ', output_names

    _reflow(workspace_names, output_names)
    if focused_workspace in non_empty_workspaces:
        go_to_workspace(focused_workspace)


if __name__ == '__main__':
    reflow_from_left_to_right()