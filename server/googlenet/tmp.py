import os
cwd = os.getcwd()
if cwd[-len("googlenet"):] == "googlenet":
    import dist_googlenet as dg
else:
    import googlenet.dist_googlenet as dg

print("success")
