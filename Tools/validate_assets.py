"""
Sanity check for the Unity YAML in this project.

It verifies that:
  * every document in the scene/prefab parses as YAML
  * every local {fileID: N} reference points at a document that exists
  * every {guid: G, fileID: F, type: T} reference points at an asset whose .meta
    uses that guid, and (for scripts) that the guid belongs to a MonoBehaviour script
  * no generator placeholders (__FOO__) are left behind

Run:  python Tools/validate_assets.py
"""
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADER_RE = re.compile(r"^--- !u!(\d+) &(-?\d+)")
LOCAL_REF_RE = re.compile(r"\{fileID: (-?\d+)\}")
ASSET_REF_RE = re.compile(r"\{fileID: (-?\d+), guid: ([0-9a-f]{32}), type: (\d+)\}")
PLACEHOLDER_RE = re.compile(r"__[A-Z_]+__")

errors = []
warnings = []

# GUIDs that belong to Unity itself or to built-in packages (com.unity.ugui).
# They are resolved by the editor, so no .meta file exists inside the project.
BUILTIN_GUIDS = {
    "0000000000000000f000000000000000": "engine default resources / sprites-default material",
    "0000000000000000e000000000000000": "engine built-in resources (LegacyRuntime font, cookie texture)",
    "5f7201a12d95ffc409449d95f23cf332": "UnityEngine.UI.Text",
    "fe87c0e1cc204ed48ad3b37840f39efc": "UnityEngine.UI.Image",
    "4e29b1a8efbd4b44bb3f3716e73f07ff": "UnityEngine.UI.Button",
    "0cd44c1031e13a943bb63640046fad76": "UnityEngine.UI.CanvasScaler",
    "dc42784cf147c0c48a680349fa168899": "UnityEngine.UI.GraphicRaycaster",
    "76c392e42b5098c458856cdf6ecaaaa1": "UnityEngine.EventSystems.EventSystem",
    "4f231c4fb786f3946a6b90b886c48677": "UnityEngine.EventSystems.StandaloneInputModule",
}


def meta_guids():
    guids = {}
    for dirpath, _dirnames, filenames in os.walk(os.path.join(ROOT, "Assets")):
        for name in filenames:
            if not name.endswith(".meta"):
                continue
            path = os.path.join(dirpath, name)
            with open(path) as f:
                text = f.read()
            m = re.search(r"^guid: ([0-9a-f]{32})$", text, re.M)
            if not m:
                errors.append("%s has no guid" % path)
                continue
            guids[m.group(1)] = (path, "MonoImporter" in text, "TextureImporter" in text)
    return guids


def load_docs(path):
    """Return the mapping fileID -> (class_id, type_name, body_text)."""
    with open(path) as f:
        text = f.read()
    docs = {}
    chunks = re.split(r"(?m)^--- !u!", text)
    for chunk in chunks[1:]:
        head, _, body = chunk.partition("\n")
        m = re.match(r"(\d+) &(-?\d+)", head)
        if not m:
            errors.append("%s: bad document header %r" % (path, head))
            continue
        class_id, file_id = m.group(1), int(m.group(2))
        body_text = body
        try:
            data = yaml.safe_load("!u!%s\n" % class_id + body) if False else yaml.safe_load(body)
        except yaml.YAMLError as exc:
            errors.append("%s: YAML error in document %s:\n%s" % (path, file_id, exc))
            data = {}
        if file_id in docs:
            errors.append("%s: duplicate fileID %d" % (path, file_id))
        docs[file_id] = (class_id, data, body_text)
    return docs


def check(path, guids):
    docs = load_docs(path)
    text = open(path).read()
    for m in PLACEHOLDER_RE.finditer(text):
        errors.append("%s: unreplaced placeholder %s" % (path, m.group(0)))

    for file_id, (class_id, data, body) in docs.items():
        if not isinstance(data, dict) or len(data) != 1:
            warnings.append("%s &%d: unexpected document shape %r" % (path, file_id, data))
            continue
        # local references
        for m in LOCAL_REF_RE.finditer(body):
            ref = int(m.group(1))
            if ref == 0:
                continue
            if ref not in docs:
                errors.append("%s &%d: local fileID %d does not exist" % (path, file_id, ref))
        # asset references
        for m in ASSET_REF_RE.finditer(body):
            ref, guid, type_id = int(m.group(1)), m.group(2), m.group(3)
            if guid in BUILTIN_GUIDS:
                if ref != 11500000 and type_id == "3" and "UI" in BUILTIN_GUIDS[guid]:
                    errors.append("%s &%d: package script must use fileID 11500000"
                                  % (path, file_id))
                continue
            if guid not in guids:
                errors.append("%s &%d: guid %s is not used by any .meta file"
                              % (path, file_id, guid))
                continue
            meta_path, is_script, is_texture = guids[guid]
            if type_id == "3" and is_script:
                if ref != 11500000:
                    errors.append("%s &%d: script reference has fileID %d (expected 11500000)"
                                  % (path, file_id, ref))
                if class_id != "114":
                    errors.append("%s &%d: script on a non-MonoBehaviour document"
                                  % (path, file_id))

    # every GameObject must be listed in the docs and have a Transform
    gameobject_ids = [fid for fid, (cid, _d, _b) in docs.items() if cid == "1"]
    for fid in gameobject_ids:
        data = docs[fid][1]["GameObject"]
        comps = [c["component"]["fileID"] for c in data["m_Component"]]
        if not any(docs[c][0] in ("4", "224") for c in comps if c in docs):
            errors.append("%s: GameObject %d has no Transform" % (path, fid))
        for c in comps:
            if c not in docs:
                errors.append("%s: GameObject %d lists missing component %d" % (path, fid, c))

    # scene root list
    if path.endswith(".unity"):
        roots = docs[max(docs)][1]["SceneRoots"]["m_Roots"]
        for entry in roots:
            tf = entry["fileID"]
            if tf not in docs:
                errors.append("%s: SceneRoots points at missing transform %d" % (path, tf))
    return docs


def main():
    check_script_fields()
    guids = meta_guids()
    print("found %d guids" % len(guids))

    scene = os.path.join(ROOT, "Assets/Scenes/Game.unity")
    prefab = os.path.join(ROOT, "Assets/Prefabs/Obstacle.prefab")
    docs = check(prefab, guids)
    print("prefab documents:", len(docs))
    docs = check(scene, guids)
    print("scene documents:", len(docs))

    # cross-check: the prefab guid used by the spawner must be the prefab's own meta guid
    prefab_meta = open(prefab + ".meta").read()
    prefab_guid = re.search(r"^guid: ([0-9a-f]{32})$", prefab_meta, re.M).group(1)
    scene_text = open(scene).read()
    if prefab_guid not in scene_text:
        errors.append("scene does not reference the Obstacle prefab guid")

    # the Obstacle tag must exist in the TagManager
    tag_manager = open(os.path.join(ROOT, "ProjectSettings/TagManager.asset")).read()
    if "- Obstacle" not in tag_manager:
        errors.append("TagManager.asset does not define the Obstacle tag")

    # The Player tag is a Unity built-in tag; make sure we only rely on built-ins.
    for builtin in ("Player", "MainCamera", "Untagged"):
        if builtin not in scene_text and builtin in ("Player", "MainCamera"):
            errors.append("scene does not use the built-in %s tag" % builtin)

    for w in warnings:
        print("WARN:", w)
    if errors:
        for e in errors:
            print("ERROR:", e)
        print("\n%d error(s)" % len(errors))
        return 1
    print("\nAll checks passed.")
    return 0




def check_script_fields():
    """Every serialized 'field:' in the scene must exist as a public field in its C# script.

    This catches the classic Unity bug where you rename a field in the script and the
    Inspector value silently disappears (or shows as 'Script file has no definition').
    """
    guid_to_script = {}
    for dirpath, _d, files in os.walk(os.path.join(ROOT, "Assets", "Scripts")):
        for name in files:
            if not name.endswith(".cs"):
                continue
            cs = os.path.join(dirpath, name)
            meta = cs + ".meta"
            guid = re.search(r"^guid: ([0-9a-f]{32})$", open(meta).read(), re.M).group(1)
            guid_to_script[guid] = cs

    scene = os.path.join(ROOT, "Assets", "Scenes", "Game.unity")
    text = open(scene).read()
    problems = 0

    # Fields every MonoBehaviour(.cs) gets from Unity itself; not declared in the script.
    UNITY_MONO_FIELDS = {"m_ObjectHideFlags", "m_CorrespondingSourceObject", "m_PrefabInstance",
                         "m_PrefabAsset", "m_GameObject", "m_Enabled", "m_EditorHideFlags",
                         "m_Script", "m_Name", "m_EditorClassIdentifier"}

    for chunk in re.split(r"^--- !u!114 &", text, flags=re.M)[1:]:
        _fid, _, body = chunk.partition("\n")
        # stop at the next document so we only look at this component's own fields
        body = re.split(r"^--- !u!", body, flags=re.M)[0]
        m = re.search(r"m_Script: \{fileID: 11500000, guid: ([0-9a-f]{32})", body)
        if not m or m.group(1) not in guid_to_script:
            continue
        cs = guid_to_script[m.group(1)]
        source = open(cs).read()
        public_fields = set(re.findall(
            r"public\s+(?!class|static|void|override)(?:[\w<>\[\],\.\s]+?)\s+(\w+)\s*(?:=|;|\{)",
            source))
        # properties (public int Score { get; ... }) serialise nothing, so ignore them
        properties = set(re.findall(r"public\s+[\w<>\[\],\.]+\s+(\w+)\s*\{", source))
        public_fields -= properties
        serialized = re.findall(r"^  (\w+):", body, re.M)
        for field in serialized:
            if field in UNITY_MONO_FIELDS or field in public_fields:
                continue
            print("ERROR: %s serialises '%s' but %s has no such public field"
                  % (os.path.basename(scene), field, os.path.basename(cs)))
            problems += 1
    if problems:
        errors.append("%d script field mismatch(es)" % problems)




if __name__ == "__main__":
    sys.exit(main())
