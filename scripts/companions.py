import re
import subprocess
from ome_model.experimental import Image, create_companion


# /uod/idr/filesets/idr0000-Strobl/Strobl2014A/DS0001/(B1)-ZStacks-ZM/CH0001/DR0003/Strobl2014A-DS0001TP0003DR0003CH0001PL(ZS).TIF
files_path = "../multitifs.txt"
pat = re.compile(r".+(?P<dataset_name>DS000\d).+/(?P<channel>CH000\d)/(?P<image_name>DR000\d)/.+(?P<timepoint>TP\d{4}).+")
root = "/uod/idr/filesets/idr0000-Strobl/Strobl2014A/"

order = "XYCZT"
img_x = 600
img_y = 1000
size_z = 150
size_c = 1
pix_type = "uint16"

t_max = dict()
with open(files_path, 'r') as read:
    for line in read.readlines():
        m = pat.match(line).groupdict()
        if m:
            key = f"{m['dataset_name']}_{m['image_name']}"
            t = int(m['timepoint'].replace("TP", "")) - 1
            if key not in t_max:
                t_max[key] = 0
            t_max[key] = max(t_max[key], t)


images = dict()
with open(files_path, 'r') as read:
    for line in read.readlines():
        m = pat.match(line).groupdict()
        if m:
            key = f"{m['dataset_name']}_{m['image_name']}"
            img_path = line.strip().replace(root, "")
            if not key in images:
                images[key] = Image(key, img_x, img_y, size_z, size_c, t_max[key]+1, order=order, type=pix_type)
                images[key].add_channel(samplesPerPixel=1)
            t = int(m['timepoint'].replace("TP", "")) - 1
            images[key].add_tiff(img_path, c=0, t=t, planeCount=size_z)

for name, image in images.items():
    companion_file = "{}.companion.ome".format(name)
    create_companion(images=[image], out=companion_file)
    proc = subprocess.Popen(
        ['xmllint', '--format', '-o', companion_file, companion_file],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)
    (output, error_output) = proc.communicate()
