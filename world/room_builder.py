from panda3d.core import (
    NodePath, CollisionNode, CollisionBox, Point3, Vec3, Vec4,
    GeomVertexFormat, GeomVertexData, GeomVertexWriter,
    Geom, GeomTriangles, GeomNode, Material,
)
from config import Masks, ROOM_SIZE, WALL_HEIGHT, WALL_THICKNESS, DOOR_WIDTH


def _make_box_geom(name, hx, hy, hz):
    fmt = GeomVertexFormat.getV3n3()
    vdata = GeomVertexData(name, fmt, Geom.UHStatic)
    vertex = GeomVertexWriter(vdata, "vertex")
    normal = GeomVertexWriter(vdata, "normal")

    faces = [
        (Vec3(0, 0, 1), [(-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]),
        (Vec3(0, 0, -1), [(-hx, hy, -hz), (hx, hy, -hz), (hx, -hy, -hz), (-hx, -hy, -hz)]),
        (Vec3(0, 1, 0), [(-hx, hy, -hz), (-hx, hy, hz), (hx, hy, hz), (hx, hy, -hz)]),
        (Vec3(0, -1, 0), [(hx, -hy, -hz), (hx, -hy, hz), (-hx, -hy, hz), (-hx, -hy, -hz)]),
        (Vec3(1, 0, 0), [(hx, -hy, -hz), (hx, hy, -hz), (hx, hy, hz), (hx, -hy, hz)]),
        (Vec3(-1, 0, 0), [(-hx, hy, -hz), (-hx, -hy, -hz), (-hx, -hy, hz), (-hx, hy, hz)]),
    ]

    for n, corners in faces:
        for c in corners:
            vertex.addData3(*c)
            normal.addData3(n)

    tris = GeomTriangles(Geom.UHStatic)
    for i in range(6):
        b = i * 4
        tris.addVertices(b, b + 1, b + 2)
        tris.addVertices(b, b + 2, b + 3)

    geom = Geom(vdata)
    geom.addPrimitive(tris)
    node = GeomNode(name)
    node.addGeom(geom)
    return node


def _make_material(color):
    mat = Material()
    mat.setDiffuse(Vec4(*color, 1))
    mat.setAmbient(Vec4(*color, 1))
    return mat


FLOOR_MAT = None
WALL_MAT = None


def _get_materials():
    global FLOOR_MAT, WALL_MAT
    if FLOOR_MAT is None:
        FLOOR_MAT = _make_material((0.35, 0.30, 0.25))
        WALL_MAT = _make_material((0.55, 0.50, 0.45))
    return FLOOR_MAT, WALL_MAT


def build_room(parent, gx, gy, openings):
    """Build a room at grid position (gx, gy) with doorways on the given sides.

    openings: set of "N", "S", "E", "W" indicating which sides have doors.
    """
    floor_mat, wall_mat = _get_materials()
    hs = ROOM_SIZE / 2
    wx = gx * ROOM_SIZE
    wy = gy * ROOM_SIZE

    root = parent.attachNewNode(f"room_{gx}_{gy}")
    root.setPos(wx, wy, 0)

    # floor
    floor_geom = _make_box_geom("floor", hs, hs, 0.05)
    floor_np = root.attachNewNode(floor_geom)
    floor_np.setPos(0, 0, -0.05)
    floor_np.setMaterial(floor_mat)

    floor_col = CollisionNode("floor_col")
    floor_col.addSolid(CollisionBox(Point3(0, 0, -0.05), hs, hs, 0.05))
    floor_col.setIntoCollideMask(Masks.FLOOR)
    floor_col.setFromCollideMask(Masks.EMPTY)
    root.attachNewNode(floor_col)

    # walls
    wh = WALL_HEIGHT / 2
    wt = WALL_THICKNESS / 2

    wall_specs = {
        "N": _north_wall_segments,
        "S": _south_wall_segments,
        "E": _east_wall_segments,
        "W": _west_wall_segments,
    }

    for side, builder in wall_specs.items():
        has_door = side in openings
        for seg in builder(hs, wh, wt, has_door):
            _place_wall(root, seg, wall_mat)

    return root


def _north_wall_segments(hs, wh, wt, has_door):
    if not has_door:
        return [("wall_n", 0, hs, wh, hs, wt, wh)]
    dh = DOOR_WIDTH / 2
    seg_len = (ROOM_SIZE - DOOR_WIDTH) / 4
    return [
        ("wall_n_l", -(dh + seg_len), hs, wh, seg_len, wt, wh),
        ("wall_n_r", (dh + seg_len), hs, wh, seg_len, wt, wh),
    ]


def _south_wall_segments(hs, wh, wt, has_door):
    if not has_door:
        return [("wall_s", 0, -hs, wh, hs, wt, wh)]
    dh = DOOR_WIDTH / 2
    seg_len = (ROOM_SIZE - DOOR_WIDTH) / 4
    return [
        ("wall_s_l", -(dh + seg_len), -hs, wh, seg_len, wt, wh),
        ("wall_s_r", (dh + seg_len), -hs, wh, seg_len, wt, wh),
    ]


def _east_wall_segments(hs, wh, wt, has_door):
    if not has_door:
        return [("wall_e", hs, 0, wh, wt, hs, wh)]
    dh = DOOR_WIDTH / 2
    seg_len = (ROOM_SIZE - DOOR_WIDTH) / 4
    return [
        ("wall_e_l", hs, -(dh + seg_len), wh, wt, seg_len, wh),
        ("wall_e_r", hs, (dh + seg_len), wh, wt, seg_len, wh),
    ]


def _west_wall_segments(hs, wh, wt, has_door):
    if not has_door:
        return [("wall_w", -hs, 0, wh, wt, hs, wh)]
    dh = DOOR_WIDTH / 2
    seg_len = (ROOM_SIZE - DOOR_WIDTH) / 4
    return [
        ("wall_w_l", -hs, -(dh + seg_len), wh, wt, seg_len, wh),
        ("wall_w_r", -hs, (dh + seg_len), wh, wt, seg_len, wh),
    ]


def _place_wall(root, seg, mat):
    name, px, py, pz, hx, hy, hz = seg

    geom = _make_box_geom(name, hx, hy, hz)
    np = root.attachNewNode(geom)
    np.setPos(px, py, pz)
    np.setMaterial(mat)

    col = CollisionNode(name + "_col")
    col.addSolid(CollisionBox(Point3(0, 0, 0), hx, hy, hz))
    col.setIntoCollideMask(Masks.WALL)
    col.setFromCollideMask(Masks.EMPTY)
    np.attachNewNode(col)
