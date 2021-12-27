import os
import json

def path_to_dict(path, parent_path=""):
    d = {'name': os.path.basename(path)}

    if (path != "."):
        d["path"] = parent_path + "/" + os.path.basename(path)

    else:
        d["path"] = "."

    if os.path.isdir(path):
        d['type'] = "directory"
        d['children'] = [path_to_dict(os.path.join(path,x), d["path"]) for x in os.listdir\
        (path) if x != ".git"]
    else:
        d['type'] = "file"
    return d

with open("tree.json", "w") as file:
    file.write( json.dumps(path_to_dict('.')) )

with open("version.txt", "r+") as file:
    version = file.read()
    file.seek(0, 0)
    file.write(version[0 : len(version) -1] + str(int(version[-1]) + 1) ) 
