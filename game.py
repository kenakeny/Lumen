import panda3d.core as p3d
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor


class myApp(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()
        properties = p3d.WindowProperties()
        properties.setTitle("Lumen")
        properties.setSize(1024, 720)
        self.win = self.openMainWindow(props=properties)
        

app = myApp()
app.run()
