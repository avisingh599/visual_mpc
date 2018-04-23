import json
import argparse
import os

import re

import pdb
parser = argparse.ArgumentParser(description='write json configuration for ngc')
parser.add_argument('run_script', type=str, help='relative path to the script to launch')
parser.add_argument('hyper', type=str, help='relative path to hyperparams file', default="")
parser.add_argument('--int', default='False', type=str, help='interactive')
parser.add_argument('--arg', default='', type=str, help='additional arguments')

args = parser.parse_args()

hyper = '/'.join(str.split(args.hyper, '/')[1:])

data = {}
data["aceName"] = "nv-us-west-2"
data["command"] = \
"cd /result && tensorboard --logdir . & \
 export VMPC_DATA_DIR=/mnt/pushing_data;\
 export TEN_DATA=/mnt/tensorflow_data;\
 export ALEX_DATA=/mnt/pretrained_models;\
 export RESULT_DIR=/result;\
 export NO_ROS='';\
 export PATH=/opt/conda/bin:/usr/local/mpi/bin:/usr/local/nvidia/bin:/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin;\
 cd /workspace/visual_mpc/docker;"

data['dockerImageName'] = "ucb_rail8888/tf_mj1.5:latest"

script_name = args.run_script

if 'benchmarks' in script_name or 'parallel_data_collection' in script_name:  #running benchmark...
    data["datasetMounts"] = [{"containerMountPoint": "/mnt/tensorflow_data/sim/mj_pos_ctrl_appflow", "id": 8906},
                             {"containerMountPoint": "/mnt/tensorflow_data/sim/appflow_nogenpix", "id": 8933},
                             {"containerMountPoint": "/mnt/tensorflow_data/sim/appflow_nogenpix_mj1.5", "id": 9006},
                             {"containerMountPoint": "/mnt/tensorflow_data/sim/cartgripper_flowonly", "id": 9007},
                             {"containerMountPoint": "/mnt/tensorflow_data/sim/mj_pos_ctrl", "id": 8930},
                             {"containerMountPoint": "/mnt/tensorflow_data/sim/pos_ctrl", "id": 8948},
                             {"containerMountPoint": "/mnt/tensorflow_data/sim/pos_ctrl_updown_rot_sact", "id": 8951},
                             {"containerMountPoint": "/mnt/tensorflow_data/sim/pos_ctrl_updown_sact", "id": 8950},
                             {"containerMountPoint": "/mnt/tensorflow_data/gdn/startgoal_shad", "id": 9087},
                             {"containerMountPoint": "/mnt/pretrained_models/bair_action_free/model.savp.transformation.flow.last_frames.2.generate_scratch_image.false.batch_size.16", "id": 9161},
                             {"containerMountPoint": "/mnt/pretrained_models/bair_action_free/model.multi_savp.ngf.64.shared_views.true.num_views.2.tv_weight.0.001.transformation.flow.last_frames.2.generate_scratch_image.false.batch_size.16", "id": 9223},
                             {"containerMountPoint": "/mnt/pushing_data/cartgripper_startgoal_masks6e4", "id": 9138},  # mj_pos_ctrl_appflow
                             {"containerMountPoint": "/mnt/pushing_data/cartgripper_startgoal_short", "id": 8949},  # mj_pos_ctrl_appflow
                             {"containerMountPoint": "/mnt/pushing_data/cartgripper_startgoal_2view", "id": 9222},  # mj_pos_ctrl_appflow
                             {"containerMountPoint": "/mnt/pushing_data/cartgripper_startgoal_masks", "id": 8914}]  # mj_pos_ctrl_appflow
    data["aceInstance"] = "ngcv8"
    command = "python " + args.run_script + " " + args.hyper + " {}".format(args.arg)

    expname = args.hyper.partition('benchmarks')[-1]
    data["name"] = '-'.join(re.compile('\w+').findall(expname + args.arg))
else:
    data["aceInstance"] = "ngcv1"
    data["datasetMounts"] = [{"containerMountPoint": "/mnt/pushing_data/cartgripper", "id": 8350},  # cartgripper
                             {"containerMountPoint": "/mnt/pushing_data/cartgripper_mj1.5", "id": 8974},
                             {"containerMountPoint": "/mnt/pushing_data/mj_pos_noreplan_fast_tfrec", "id": 8807},  #mj_pos_noreplan_fast_tfrec    | gtruth mujoco planning pushing
                             {"containerMountPoint": "/mnt/pushing_data/mj_pos_noreplan_fast_tfrec_fewdata", "id": 8972},  #mj_pos_noreplan_fast_tfrec    | gtruth mujoco planning pushing
                             {"containerMountPoint": "/mnt/pushing_data/cartgripper_updown_sact", "id": 8950},
                             {"containerMountPoint": "/mnt/pushing_data/cartgripper_updown_rot_sact", "id": 8951}]

    command = "python " + args.run_script + " --hyper ../../" + hyper
    data["name"] = str.split(command, '/')[-2]

if args.int == 'True':
    command = "/bin/sleep 36000"
    data["name"] += 'int'
data["command"] += command

data["resultContainerMountPoint"] = "/result"
data["publishedContainerPorts"] = [6006] #for tensorboard

with open('autogen.json', 'w') as outfile:
    json.dump(data, outfile, indent=4)

os.system("ngc batch run -f autogen.json")
