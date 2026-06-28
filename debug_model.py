from direct.showbase.ShowBase import ShowBase
import panda3d.core as p3d

app = ShowBase()
model = app.loader.loadModel("assets/models/Kenpachi.glb")
model.reparentTo(app.render)

# Print raw bounds before any transform
bounds = model.getTightBounds()
if bounds:
    mn, mx = bounds
    print(f"Min: {mn}")
    print(f"Max: {mx}")
    print(f"Size: {mx - mn}")
    print(f"Center: {(mn + mx) / 2}")
else:
    print("No bounds found")

# List child nodes
for child in model.getChildren():
    print(f"Child: {child.getName()}")
    cb = child.getTightBounds()
    if cb:
        cmn, cmx = cb
        print(f"  Size: {cmx - cmn}")

app.destroy()
