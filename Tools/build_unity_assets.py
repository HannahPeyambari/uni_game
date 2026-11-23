"""
Generates the Unity .meta files (GUIDs) and the Game scene + Obstacle prefab YAML.

Everything this writes is already committed to the repository. Run it only if you
change the layout and want the scene regenerated deterministically:

    python Tools/build_unity_assets.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Fixed GUIDs, so the .meta files and the references inside the scene agree.
# ---------------------------------------------------------------------------
GUID = {
    "Assets/Scripts/GameManager.cs": "3a91b1c0e1a14b8b9d0a1c42f5b7d001",
    "Assets/Scripts/PlayerController.cs": "3a91b1c0e1a14b8b9d0a1c42f5b7d002",
    "Assets/Scripts/PlayerCollision.cs": "3a91b1c0e1a14b8b9d0a1c42f5b7d003",
    "Assets/Scripts/ObstacleMover.cs": "3a91b1c0e1a14b8b9d0a1c42f5b7d004",
    "Assets/Scripts/ObstacleSpawner.cs": "3a91b1c0e1a14b8b9d0a1c42f5b7d005",
    "Assets/Scripts/BackgroundScroller.cs": "3a91b1c0e1a14b8b9d0a1c42f5b7d006",
    "Assets/Scripts": "3a91b1c0e1a14b8b9d0a1c42f5b7d010",
    "Assets/Scenes": "3a91b1c0e1a14b8b9d0a1c42f5b7d011",
    "Assets/Prefabs": "3a91b1c0e1a14b8b9d0a1c42f5b7d012",
    "Assets/Art": "3a91b1c0e1a14b8b9d0a1c42f5b7d013",
    "Assets/Art/Sprites": "3a91b1c0e1a14b8b9d0a1c42f5b7d014",
    "Assets/Scenes/Game.unity": "2f9d1c4a7b6e48f4a9c2d35e8b1f7a60",
    "Assets/Prefabs/Obstacle.prefab": "3a91b1c0e1a14b8b9d0a1c42f5b7d020",
    "Assets/Art/Sprites/Player.png": "3a91b1c0e1a14b8b9d0a1c42f5b7d101",
    "Assets/Art/Sprites/Obstacle.png": "3a91b1c0e1a14b8b9d0a1c42f5b7d102",
    "Assets/Art/Sprites/Ground.png": "3a91b1c0e1a14b8b9d0a1c42f5b7d103",
    "Assets/Art/Sprites/SkyGradient.png": "3a91b1c0e1a14b8b9d0a1c42f5b7d104",
    "Assets/Art/Sprites/UIRoundedBox.png": "3a91b1c0e1a14b8b9d0a1c42f5b7d105",
    "Assets/Art/Sprites/Cloud.png": "3a91b1c0e1a14b8b9d0a1c42f5b7d106",
    "Assets/Art/Sprites/GroundGrass.png": "3a91b1c0e1a14b8b9d0a1c42f5b7d107",
}

# fileID of the Obstacle prefab's root GameObject. The scene's obstaclePrefab field and
# the prefab itself must agree on this exact number, otherwise Unity silently nulls the
# reference (symptom: no obstacles spawn, plus InvalidCastException in the console).
PREFAB_ROOT_ID = 100100000

UGUI_TEXT = "5f7201a12d95ffc409449d95f23cf332"
UGUI_IMAGE = "fe87c0e1cc204ed48ad3b37840f39efc"
UGUI_BUTTON = "4e29b1a8efbd4b44bb3f3716e73f07ff"
UGUI_CANVAS_SCALER = "0cd44c1031e13a943bb63640046fad76"
UGUI_RAYCASTER = "dc42784cf147c0c48a680349fa168899"

# Unity's built-in LegacyRuntime/Arial font. fileID 10102 with the engine's own
# guid is how real 2022.1 scenes point at it, so no .meta file is needed.
BUILTIN_FONT = {10102}

DEFAULT_SPRITE_MAT = "{fileID: 10754, guid: 0000000000000000f000000000000000, type: 0}"
HEAD = "%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n"


def write(rel_path, text):
    path = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\n") as f:
        f.write(text)
    print("wrote", rel_path)


def fmt(v):
    """Unity writes numbers with a '.' decimal separator and no trailing zeros."""
    if isinstance(v, float):
        if v == int(v):
            return str(int(v))
        text = ("%.6f" % v).rstrip("0").rstrip(".")
    else:
        text = str(v)
    return text.replace(",", ".")   # never emit a comma decimal separator


def vec(x, y, z=0.0):
    return "{x: %s, y: %s, z: %s}" % (fmt(x), fmt(y), fmt(z))


def yaml_str(text):
    """Quote a string the way Unity's YAML writer does when it needs to."""
    if text == "":
        return " "
    if any(ch in text for ch in ":#{}[]&*!|>'\"%@`") or text != text.strip():
        return "'" + text.replace("'", "''") + "'"
    return text


def color(c):
    return "{r: %s, g: %s, b: %s, a: %s}" % tuple(fmt(v) for v in c)


def fref(fid, guid=None, type_id=3):
    if guid is None:
        return "{fileID: %d}" % fid
    return "{fileID: %d, guid: %s, type: %d}" % (fid, guid, type_id)


# ---------------------------------------------------------------------------
# .meta files
# ---------------------------------------------------------------------------
def script_meta(guid):
    return ("fileFormatVersion: 2\nguid: %s\nMonoImporter:\n  externalObjects: {}\n"
            "  serializedVersion: 2\n  defaultReferences: []\n  executionOrder: 0\n"
            "  icon: {instanceID: 0}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n"
            % guid)


def folder_meta(guid):
    return ("fileFormatVersion: 2\nguid: %s\nfolderAsset: yes\nDefaultImporter:\n"
            "  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n"
            % guid)


def importer_meta(guid, importer):
    return ("fileFormatVersion: 2\nguid: %s\n%s:\n  externalObjects: {}\n  userData: \n"
            "  assetBundleName: \n  assetBundleVariant: \n" % (guid, importer))


def sprite_meta(guid, pixels_per_unit=100, repeat=False, border=0):
    wrap = 0 if repeat else 1
    return (
        "fileFormatVersion: 2\n"
        "guid: %s\n"
        "TextureImporter:\n"
        "  internalIDToNameTable: []\n"
        "  externalObjects: {}\n"
        "  serializedVersion: 11\n"
        "  mipmaps:\n"
        "    mipMapMode: 0\n"
        "    enableMipMap: 0\n"
        "    sRGBTexture: 1\n"
        "    linearTexture: 0\n"
        "    fadeOut: 0\n"
        "    borderMipMap: 0\n"
        "    mipMapsPreserveCoverage: 0\n"
        "    alphaTestReferenceValue: 0.5\n"
        "    mipMapFadeDistanceStart: 1\n"
        "    mipMapFadeDistanceEnd: 3\n"
        "  bumpmap:\n"
        "    convertToNormalMap: 0\n"
        "    externalNormalMap: 0\n"
        "    heightScale: 0.25\n"
        "    normalMapFilter: 0\n"
        "    flipGreenChannel: 0\n"
        "  isReadable: 0\n"
        "  streamingMipmaps: 0\n"
        "  streamingMipmapsPriority: 0\n"
        "  vTOnly: 0\n"
        "  ignoreMasterTextureLimit: 0\n"
        "  grayScaleToAlpha: 0\n"
        "  generateCubemap: 6\n"
        "  cubemapConvolution: 0\n"
        "  seamlessCubemap: 0\n"
        "  textureFormat: 1\n"
        "  maxTextureSize: 2048\n"
        "  textureSettings:\n"
        "    serializedVersion: 2\n"
        "    filterMode: 1\n"
        "    aniso: 1\n"
        "    mipBias: 0\n"
        "    wrapU: %d\n"
        "    wrapV: %d\n"
        "    wrapW: 0\n"
        "  nPOTScale: 0\n"
        "  lightmap: 0\n"
        "  compressionQuality: 50\n"
        "  spriteMode: 1\n"
        "  spriteExtrude: 1\n"
        "  spriteMeshType: 1\n"
        "  alignment: 0\n"
        "  spritePivot: {x: 0.5, y: 0.5}\n"
        "  spritePixelsToUnits: %d\n"
        "  spriteBorder: {x: %d, y: %d, z: %d, w: %d}\n"
        "  spriteGenerateFallbackPhysicsShape: 1\n"
        "  alphaUsage: 1\n"
        "  alphaIsTransparency: 1\n"
        "  spriteTessellationDetail: -1\n"
        "  textureType: 8\n"
        "  textureShape: 1\n"
        "  singleChannelComponent: 0\n"
        "  flipbookRows: 1\n"
        "  flipbookColumns: 1\n"
        "  maxTextureSizeSet: 0\n"
        "  compressionQualitySet: 0\n"
        "  textureFormatSet: 0\n"
        "  ignorePngGamma: 0\n"
        "  applyGammaDecoding: 0\n"
        "  swizzle: 50462976\n"
        "  platformSettings:\n"
        "  - serializedVersion: 3\n"
        "    buildTarget: DefaultTexturePlatform\n"
        "    maxTextureSize: 2048\n"
        "    resizeAlgorithm: 0\n"
        "    textureFormat: -1\n"
        "    textureCompression: 1\n"
        "    compressionQuality: 50\n"
        "    crunchedCompression: 0\n"
        "    allowsAlphaSplitting: 0\n"
        "    overridden: 0\n"
        "    androidETC2FallbackOverride: 0\n"
        "    forceMaximumCompressionQuality_BC6H_BC7: 0\n"
        "  spriteSheet:\n"
        "    serializedVersion: 2\n"
        "    sprites: []\n"
        "    outline: []\n"
        "    physicsShape: []\n"
        "    bones: []\n"
        "    spriteID: \n"
        "    internalID: 0\n"
        "    vertices: []\n"
        "    indices: \n"
        "    edges: []\n"
        "    weights: []\n"
        "    secondaryTextures: []\n"
        "  spritePackingTag: \n"
        "  pSDRemoveMatte: 0\n"
        "  userData: \n"
        "  assetBundleName: \n"
        "  assetBundleVariant: \n" % (guid, wrap, wrap, pixels_per_unit,
                                    border, border, border, border)
    )


def write_metas():
    for rel, guid in GUID.items():
        if os.path.isdir(os.path.join(ROOT, rel)):
            write(rel + ".meta", folder_meta(guid))
        elif rel.endswith(".cs"):
            write(rel + ".meta", script_meta(guid))
        elif rel.endswith(".unity"):
            write(rel + ".meta", importer_meta(guid, "DefaultImporter"))
        elif rel.endswith(".prefab"):
            write(rel + ".meta", importer_meta(guid, "PrefabImporter"))
        elif rel.endswith(".png"):
            repeat = rel.endswith(("Ground.png", "GroundGrass.png", "SkyGradient.png"))
            # The UI box is 9-sliced, so Unity needs to know its corner size.
            border = 10 if rel.endswith("UIRoundedBox.png") else 0
            write(rel + ".meta", sprite_meta(guid, 1 if "Sky" in rel else 100,
                                             repeat, border))


# ---------------------------------------------------------------------------
# Tiny component factories. Each returns (class_id, type_name, body).
# %GOID% is replaced with the owning GameObject's fileID.
# ---------------------------------------------------------------------------
def _header():
    return ("  m_ObjectHideFlags: 0\n"
            "  m_CorrespondingSourceObject: {fileID: 0}\n"
            "  m_PrefabInstance: {fileID: 0}\n"
            "  m_PrefabAsset: {fileID: 0}\n"
            "  m_GameObject: {fileID: %GOID%}\n")


def c_transform():
    return None  # transforms are emitted by the builder


def c_sprite(sprite_guid, color_=(1, 1, 1, 1), order=0, draw_mode=0, size=(1, 1)):
    body = (_header() +
            "  m_Enabled: 1\n"
            "  m_CastShadows: 0\n"
            "  m_ReceiveShadows: 0\n"
            "  m_DynamicOccludee: 1\n"
            "  m_StaticShadowCaster: 0\n"
            "  m_MotionVectors: 1\n"
            "  m_LightProbeUsage: 1\n"
            "  m_ReflectionProbeUsage: 1\n"
            "  m_RayTracingMode: 0\n"
            "  m_RayTraceProcedural: 0\n"
            "  m_RenderingLayerMask: 1\n"
            "  m_RendererPriority: 0\n"
            "  m_Materials:\n"
            "  - " + DEFAULT_SPRITE_MAT + "\n"
            "  m_StaticBatchInfo:\n"
            "    firstSubMesh: 0\n"
            "    subMeshCount: 0\n"
            "  m_StaticBatchRoot: {fileID: 0}\n"
            "  m_ProbeAnchor: {fileID: 0}\n"
            "  m_LightProbeVolumeOverride: {fileID: 0}\n"
            "  m_ScaleInLightmap: 1\n"
            "  m_ReceiveGI: 1\n"
            "  m_PreserveUVs: 0\n"
            "  m_IgnoreNormalsForChartDetection: 0\n"
            "  m_ImportantGI: 0\n"
            "  m_StitchLightmapSeams: 1\n"
            "  m_SelectedEditorRenderState: 0\n"
            "  m_MinimumChartSize: 4\n"
            "  m_AutoUVMaxDistance: 0.5\n"
            "  m_AutoUVMaxAngle: 89\n"
            "  m_LightmapParameters: {fileID: 0}\n"
            "  m_SortingLayerID: 0\n"
            "  m_SortingLayer: 0\n"
            "  m_SortingOrder: %d\n"
            "  m_Sprite: %s\n"
            "  m_Color: %s\n"
            "  m_FlipX: 0\n"
            "  m_FlipY: 0\n"
            "  m_DrawMode: %d\n"
            "  m_Size: {x: %s, y: %s}\n"
            "  m_AdaptiveModeThreshold: 0.5\n"
            "  m_SpriteTileMode: 0\n"
            "  m_WasSpriteAssigned: 1\n"
            "  m_MaskInteraction: 0\n"
            "  m_SpriteSortPoint: %d\n"
            % (order, fref(21300000, sprite_guid), color(color_), draw_mode,
               fmt(size[0]), fmt(size[1]), 1 if draw_mode == 2 else 0))
    return ("212", "SpriteRenderer", body)


def c_box_collider(size, offset=(0, 0), trigger=False, physics_mat=None):
    body = (_header() +
            "  m_Enabled: 1\n"
            "  m_Density: 1\n"
            "  m_Material: %s\n"
            "  m_IncludeLayers:\n    serializedVersion: 2\n    m_Bits: 0\n"
            "  m_ExcludeLayers:\n    serializedVersion: 2\n    m_Bits: 0\n"
            "  m_LayerOverridePriority: 0\n"
            "  m_ForceSendLayers:\n    serializedVersion: 2\n    m_Bits: 4294967295\n"
            "  m_ForceReceiveLayers:\n    serializedVersion: 2\n    m_Bits: 4294967295\n"
            "  m_ContactCaptureLayers:\n    serializedVersion: 2\n    m_Bits: 4294967295\n"
            "  m_CallbackLayers:\n    serializedVersion: 2\n    m_Bits: 4294967295\n"
            "  m_IsTrigger: %d\n"
            "  m_UsedByEffector: 0\n"
            "  m_UsedByComposite: 0\n"
            "  m_Offset: {x: %s, y: %s}\n"
            "  m_SpriteTilingProperty:\n"
            "    border: {x: 0, y: 0, z: 0, w: 0}\n"
            "    pivot: {x: 0.5, y: 0.5}\n"
            "    oldSize: {x: 1, y: 1}\n"
            "    newSize: {x: 1, y: 1}\n"
            "    adaptiveTilingThreshold: 0.5\n"
            "    drawMode: 0\n"
            "    adaptiveTiling: 0\n"
            "  m_AutoTiling: 0\n"
            "  m_Size: {x: %s, y: %s}\n"
            "  m_EdgeRadius: 0\n"
            % (fref(0) if physics_mat is None else fref(6200000, physics_mat, 2),
               1 if trigger else 0, fmt(offset[0]), fmt(offset[1]),
               fmt(size[0]), fmt(size[1])))
    return ("61", "BoxCollider2D", body)


def c_rigidbody2d(body_type=1, gravity=1.0, constraints=0, interpolation=0, detection=0, mass=1.0):
    body = (_header() +
            "  serializedVersion: 4\n"
            "  m_BodyType: %d\n"
            "  m_Simulated: 1\n"
            "  m_UseFullKinematicContacts: 0\n"
            "  m_UseAutoMass: 0\n"
            "  m_Mass: %s\n"
            "  m_LinearDrag: 0\n"
            "  m_AngularDrag: 0.05\n"
            "  m_GravityScale: %s\n"
            "  m_Material: {fileID: 0}\n"
            "  m_IncludeLayers:\n    serializedVersion: 2\n    m_Bits: 0\n"
            "  m_ExcludeLayers:\n    serializedVersion: 2\n    m_Bits: 0\n"
            "  m_Interpolate: %d\n"
            "  m_SleepingMode: 1\n"
            "  m_CollisionDetection: %d\n"
            "  m_Constraints: %d\n"
            % (body_type, fmt(mass), fmt(gravity), interpolation, detection, constraints))
    return ("50", "Rigidbody2D", body)


def c_mono(script_guid, fields=""):
    body = (_header() +
            "  m_Enabled: 1\n"
            "  m_EditorHideFlags: 0\n"
            "  m_Script: {fileID: 11500000, guid: %s, type: 3}\n"
            "  m_Name: \n"
            "  m_EditorClassIdentifier: \n" % script_guid)
    return ("114", "MonoBehaviour", body + fields)


def c_camera(ortho_size=5.0, background=(0.55, 0.78, 0.95, 1)):
    body = (_header() +
            "  m_Enabled: 1\n"
            "  serializedVersion: 2\n"
            "  m_ClearFlags: 2\n"
            "  m_BackGroundColor: %s\n"
            "  m_projectionMatrixMode: 1\n"
            "  m_GateFitMode: 2\n"
            "  m_FOVAxisMode: 0\n"
            "  m_SensorSize: {x: 36, y: 24}\n"
            "  m_LensShift: {x: 0, y: 0}\n"
            "  m_FocalLength: 50\n"
            "  m_NormalizedViewPortRect:\n"
            "    serializedVersion: 2\n"
            "    x: 0\n    y: 0\n    width: 1\n    height: 1\n"
            "  near clip plane: 0.3\n"
            "  far clip plane: 1000\n"
            "  field of view: 60\n"
            "  orthographic: 1\n"
            "  orthographic size: %s\n"
            "  m_Depth: -1\n"
            "  m_CullingMask:\n    serializedVersion: 2\n    m_Bits: 4294967295\n"
            "  m_RenderingPath: -1\n"
            "  m_TargetTexture: {fileID: 0}\n"
            "  m_TargetDisplay: 0\n"
            "  m_TargetEye: 3\n"
            "  m_HDR: 1\n"
            "  m_AllowMSAA: 1\n"
            "  m_AllowDynamicResolution: 0\n"
            "  m_ForceIntoRT: 0\n"
            "  m_OcclusionCulling: 0\n"
            "  m_StereoConvergence: 10\n"
            "  m_StereoSeparation: 0.022\n"
            % (color(background), fmt(ortho_size)))
    return ("20", "Camera", body)


def c_audio_listener():
    return ("81", "AudioListener", _header() + "  m_Enabled: 1\n")


def c_canvas():
    body = (_header() +
            "  m_Enabled: 1\n"
            "  serializedVersion: 3\n"
            "  m_RenderMode: 0\n"
            "  m_Camera: {fileID: 0}\n"
            "  m_PlaneDistance: 100\n"
            "  m_PixelPerfect: 0\n"
            "  m_ReceivesEvents: 1\n"
            "  m_OverrideSorting: 0\n"
            "  m_OverridePixelPerfect: 0\n"
            "  m_SortingBucketNormalizedSize: 0\n"
            "  m_VertexColorAlwaysGammaSpace: 0\n"
            "  m_AdditionalShaderChannelsFlag: 25\n"
            "  m_UpdateRectTransformForStandalone: 0\n"
            "  m_SortingLayerID: 0\n"
            "  m_SortingOrder: 0\n"
            "  m_TargetDisplay: 0\n")
    return ("223", "Canvas", body)


def c_canvas_scaler(ref_w, ref_h, match=0.5):
    body = (_header() +
            "  m_Enabled: 1\n"
            "  m_EditorHideFlags: 0\n"
            "  m_Script: {fileID: 11500000, guid: %s, type: 3}\n"
            "  m_Name: \n"
            "  m_EditorClassIdentifier: \n"
            "  m_UiScaleMode: 1\n"
            "  m_ReferencePixelsPerUnit: 100\n"
            "  m_ScaleFactor: 1\n"
            "  m_ReferenceResolution: {x: %s, y: %s}\n"
            "  m_ScreenMatchMode: 0\n"
            "  m_MatchWidthOrHeight: %s\n"
            "  m_PhysicalUnit: 3\n"
            "  m_FallbackScreenDPI: 96\n"
            "  m_DefaultSpriteDPI: 96\n"
            "  m_DynamicPixelsPerUnit: 1\n"
            "  m_PresetInfoIsWorld: 0\n" % (UGUI_CANVAS_SCALER, fmt(ref_w), fmt(ref_h), fmt(match)))
    return ("114", "MonoBehaviour", body)


def c_raycaster():
    body = (_header() +
            "  m_Enabled: 1\n"
            "  m_EditorHideFlags: 0\n"
            "  m_Script: {fileID: 11500000, guid: %s, type: 3}\n"
            "  m_Name: \n"
            "  m_EditorClassIdentifier: \n"
            "  m_IgnoreReversedGraphics: 1\n"
            "  m_BlockingObjects: 0\n"
            "  m_BlockingMask:\n    serializedVersion: 2\n    m_Bits: 4294967295\n"
            % UGUI_RAYCASTER)
    return ("114", "MonoBehaviour", body)


def c_event_system():
    body = (_header() +
            "  m_Enabled: 1\n"
            "  m_EditorHideFlags: 0\n"
            "  m_Script: {fileID: 11500000, guid: 76c392e42b5098c458856cdf6ecaaaa1, type: 3}\n"
            "  m_Name: \n"
            "  m_EditorClassIdentifier: \n"
            "  m_FirstSelected: {fileID: 0}\n"
            "  m_sendNavigationEvents: 1\n"
            "  m_DragThreshold: 10\n")
    return ("114", "MonoBehaviour", body)


def c_standalone_input_module():
    body = (_header() +
            "  m_Enabled: 1\n"
            "  m_EditorHideFlags: 0\n"
            "  m_Script: {fileID: 11500000, guid: 4f231c4fb786f3946a6b90b886c48677, type: 3}\n"
            "  m_Name: \n"
            "  m_EditorClassIdentifier: \n"
            "  m_SendPointerHoverToParent: 1\n"
            "  m_HorizontalAxis: Horizontal\n"
            "  m_VerticalAxis: Vertical\n"
            "  m_SubmitButton: Submit\n"
            "  m_CancelButton: Cancel\n"
            "  m_InputActionsPerSecond: 10\n"
            "  m_RepeatDelay: 0.5\n"
            "  m_ForceModuleActive: 0\n")
    return ("114", "MonoBehaviour", body)


def c_canvas_renderer():
    return ("222", "CanvasRenderer", _header() + "  m_CullTransparentMesh: 1\n")


def c_image(sprite_guid, color_=(1, 1, 1, 1), image_type=1, fill_center=1, raycast=True):
    body = (_header() +
            "  m_Enabled: 1\n"
            "  m_EditorHideFlags: 0\n"
            "  m_Script: {fileID: 11500000, guid: %s, type: 3}\n"
            "  m_Name: \n"
            "  m_EditorClassIdentifier: \n"
            "  m_Material: {fileID: 0}\n"
            "  m_Color: %s\n"
            "  m_RaycastTarget: %d\n"
            "  m_RaycastPadding: {x: 0, y: 0, z: 0, w: 0}\n"
            "  m_Maskable: 1\n"
            "  m_OnCullStateChanged:\n"
            "    m_PersistentCalls:\n"
            "      m_Calls: []\n"
            "  m_Sprite: %s\n"
            "  m_Type: %d\n"
            "  m_PreserveAspect: 0\n"
            "  m_FillCenter: %d\n"
            "  m_FillMethod: 4\n"
            "  m_FillAmount: 1\n"
            "  m_FillClockwise: 1\n"
            "  m_FillOrigin: 0\n"
            "  m_UseSpriteMesh: 0\n"
            "  m_PixelsPerUnitMultiplier: 1\n"
            % (UGUI_IMAGE, color(color_), 1 if raycast else 0,
               fref(21300000, sprite_guid) if sprite_guid else fref(0), image_type, fill_center))
    return ("114", "MonoBehaviour", body)


def c_text(text, font_size=40, anchor=4, align=4, color_=(1, 1, 1, 1),
           h_overflow=1, v_overflow=1, best_fit=False, min_size=10, max_size=200,
           style=1, raycast=False, line_spacing=1.0):
    body = (_header() +
            "  m_Enabled: 1\n"
            "  m_EditorHideFlags: 0\n"
            "  m_Script: {fileID: 11500000, guid: %s, type: 3}\n"
            "  m_Name: \n"
            "  m_EditorClassIdentifier: \n"
            "  m_Material: {fileID: 0}\n"
            "  m_Color: %s\n"
            "  m_RaycastTarget: %d\n"
            "  m_RaycastPadding: {x: 0, y: 0, z: 0, w: 0}\n"
            "  m_Maskable: 1\n"
            "  m_OnCullStateChanged:\n"
            "    m_PersistentCalls:\n"
            "      m_Calls: []\n"
            "  m_FontData:\n"
            "    m_Font: %s\n"
            "    m_FontSize: %d\n"
            "    m_FontStyle: %d\n"
            "    m_BestFit: %d\n"
            "    m_MinSize: %d\n"
            "    m_MaxSize: %d\n"
            "    m_Alignment: %d\n"
            "    m_AlignByGeometry: 0\n"
            "    m_RichText: 1\n"
            "    m_HorizontalOverflow: %d\n"
            "    m_VerticalOverflow: %d\n"
            "    m_LineSpacing: %s\n"
            "  m_Text: %s\n"
            % (UGUI_TEXT, color(color_), 1 if raycast else 0,
               fref(10102, "0000000000000000e000000000000000", 0),
               font_size, style, 1 if best_fit else 0, min_size, max_size, align,
               h_overflow, v_overflow, fmt(line_spacing), yaml_str(text)))
    return ("114", "MonoBehaviour", body)


def c_button(target_graphic_id, onclick_lines):
    body = (_header() +
            "  m_Enabled: 1\n"
            "  m_EditorHideFlags: 0\n"
            "  m_Script: {fileID: 11500000, guid: %s, type: 3}\n"
            "  m_Name: \n"
            "  m_EditorClassIdentifier: \n"
            "  m_Navigation:\n"
            "    m_Mode: 3\n"
            "    m_WrapAround: 0\n"
            "    m_SelectOnUp: {fileID: 0}\n"
            "    m_SelectOnDown: {fileID: 0}\n"
            "    m_SelectOnLeft: {fileID: 0}\n"
            "    m_SelectOnRight: {fileID: 0}\n"
            "  m_Transition: 1\n"
            "  m_Colors:\n"
            "    m_NormalColor: {r: 1, g: 1, b: 1, a: 1}\n"
            "    m_HighlightedColor: {r: 0.9607843, g: 0.9607843, b: 0.9607843, a: 1}\n"
            "    m_PressedColor: {r: 0.78431374, g: 0.78431374, b: 0.78431374, a: 1}\n"
            "    m_SelectedColor: {r: 0.9607843, g: 0.9607843, b: 0.9607843, a: 1}\n"
            "    m_DisabledColor: {r: 0.78431374, g: 0.78431374, b: 0.78431374, a: 0.5019608}\n"
            "    m_ColorMultiplier: 1\n"
            "    m_FadeDuration: 0.1\n"
            "  m_SpriteState:\n"
            "    m_HighlightedSprite: {fileID: 0}\n"
            "    m_PressedSprite: {fileID: 0}\n"
            "    m_SelectedSprite: {fileID: 0}\n"
            "    m_DisabledSprite: {fileID: 0}\n"
            "  m_AnimationTriggers:\n"
            "    m_NormalTrigger: Normal\n"
            "    m_HighlightedTrigger: Highlighted\n"
            "    m_PressedTrigger: Pressed\n"
            "    m_SelectedTrigger: Selected\n"
            "    m_DisabledTrigger: Disabled\n"
            "  m_Interactable: 1\n"
            "  m_TargetGraphic: %s\n"
            "  m_OnClick:\n"
            "    m_PersistentCalls:\n"
            "      m_Calls:\n" % (UGUI_BUTTON, fref(target_graphic_id)) + onclick_lines)
    return ("114", "MonoBehaviour", body)


# ---------------------------------------------------------------------------
# Object model
# ---------------------------------------------------------------------------
class Obj:
    """A GameObject. Paths like "Canvas/GameOverPanel" are used for cross references."""

    def __init__(self, name, path, parent=None, pos=(0, 0, 0), scale=(1, 1, 1),
                 tag="Untagged", active=True, rect=None):
        self.name = name
        self.path = path
        self.parent = parent
        self.children = []
        self.pos = pos
        self.scale = scale
        self.tag = tag
        self.active = active
        self.rect = rect
        self.id = None
        self.transform_id = None
        self.comps = []          # (class_id, type_name, body, file_id)
        if parent is not None:
            parent.children.append(self)

    def add(self, comp):
        if comp is None:
            return None
        class_id, type_name, body = comp
        self.comps.append([class_id, type_name, body, None])
        return len(self.comps) - 1

    def comp_id(self, index):
        return self.comps[index][3]


SCENE_OBJS = []


def root(name, **kw):
    o = Obj(name, name, None, **kw)
    SCENE_OBJS.append(o)
    return o


def rect(name, parent, amin, amax, size, apos=(0, 0), pivot=(0.5, 0.5), **kw):
    path = parent.path + "/" + name
    return Obj(name, path, parent, rect=dict(amin=amin, amax=amax, size=size,
                                             apos=apos, pivot=pivot), **kw)


# ---------------------------------------------------------------------------
# Scene
# ---------------------------------------------------------------------------
def build_scene():
    del SCENE_OBJS[:]
    by_path = {}

    # ---------------- camera ----------------
    cam = root("Main Camera", tag="MainCamera", pos=(0, 0, -10))
    cam.add(c_camera(ortho_size=6.0, background=(0.62, 0.83, 0.98, 1)))
    cam.add(c_audio_listener())

    # ---------------- background sky strip ----------------
    # Sky: an 8 x 256 px gradient imported at 1 pixel per unit, so it is 8 x 256 units
    # before scaling. These scales stretch it to exactly 16 x 12 units, which covers the
    # whole camera view (orthographic size 6). No scroller here: the sky never moves.
    sky = root("Background", pos=(0, 0, 1), scale=(2, 0.046875, 1))
    sky.add(c_sprite(GUID["Assets/Art/Sprites/SkyGradient.png"], (1, 1, 1, 1), order=-100))

    # ---------------- decorative clouds ----------------
    cloud_guid = GUID["Assets/Art/Sprites/Cloud.png"]
    for i, (x, y, s) in enumerate([(-6.5, 2.6, 1.3), (1.0, 3.6, 1.0), (7.0, 2.0, 1.1)]):
        cloud = root("Cloud %d" % (i + 1), pos=(x, y, 2), scale=(s, s, 1))
        cloud.add(c_sprite(cloud_guid, (1, 1, 1, 0.85), order=-50))
        cloud.add(c_mono(GUID["Assets/Scripts/BackgroundScroller.cs"],
                         "  speed: 0.9\n  wrapDistance: 22\n"))

    # ---------------- ground ----------------
    # The ground collider's top edge is at y = -2, so the player's feet land on it.
    # Two sprites draw it: a dirt fill and a grass strip along the top.
    ground = root("Ground", pos=(0, -8, 0))
    ground.add(c_sprite(GUID["Assets/Art/Sprites/Ground.png"], (1, 1, 1, 1),
                        order=-10, draw_mode=2, size=(60, 12)))
    ground.add(c_box_collider((60, 12)))

    grass = root("GroundGrass", pos=(0, -2, -0.5))
    grass.add(c_sprite(GUID["Assets/Art/Sprites/GroundGrass.png"], (1, 1, 1, 1),
                       order=-9, draw_mode=2, size=(60, 0.24)))

    # ---------------- player ----------------
    player = root("Player", tag="Player", pos=(-6, -1.5, 0))
    # SpriteRenderer(_sprite), BoxCollider2D(_col), Rigidbody2D(_rb),
    # PlayerController, PlayerCollision
    player.add(c_sprite(GUID["Assets/Art/Sprites/Player.png"], (1, 1, 1, 1), order=10))
    player.add(c_box_collider((1, 1)))
    # Rigidbody2D: body 0 = Dynamic, gravity 1, constraints 4 = FreezeRotation
    player.add(c_rigidbody2d(body_type=0, gravity=2.2, constraints=4,
                             interpolation=1, detection=1, mass=1))
    player.add(c_mono(GUID["Assets/Scripts/PlayerController.cs"],
                      "  jumpForce: 12\n"
                      "  groundCheckDistance: 0.12\n"
                      "  groundLayers:\n"
                      "    serializedVersion: 2\n"
                      "    m_Bits: 4294967295\n"
                      "  useMouseAndTouch: 1\n"
                      "  useSpaceBar: 1\n"))
    player.add(c_mono(GUID["Assets/Scripts/PlayerCollision.cs"],
                      "  obstacleTag: Obstacle\n"))

    # ---------------- spawner ----------------
    spawner = root("ObstacleSpawner", pos=(0, 0, 0))
    # Obstacles sit in the lower third of the screen, so a 3-unit jump always clears them.
    spawner.add(c_mono(GUID["Assets/Scripts/ObstacleSpawner.cs"],
                       "  obstaclePrefab: %s\n"
                       "  spawnX: 11\n"
                       "  minY: -1.4\n"
                       "  maxY: -0.4\n"
                       "  startSpawnInterval: 1.7\n"
                       "  minSpawnInterval: 0.85\n"
                       "  intervalStepPerSecond: 0.02\n"
                       "  startSpeed: 4.5\n"
                       "  speedIncreasePerSecond: 0.3\n"
                       "  maxSpeed: 15\n"
                       % "__PREFAB__"))

    # ---------------- GameManager ----------------
    gm = root("GameManager", pos=(0, 0, 0))
    gm.add(c_mono(GUID["Assets/Scripts/GameManager.cs"],
                  "  player: __PLAYER__\n"
                  "  spawner: __SPAWNER__\n"
                  "  scoreText: __SCORETEXT__\n"
                  "  gameOverPanel: __GAMEOVERPANEL__\n"
                  "  finalScoreText: __FINALSCORE__\n"
                  "  tapToStartText: __TAPTOSTART__\n"
                  "  bestScoreText: __BESTSCORE__\n"
                  "  onGameOver:\n"
                  "    m_PersistentCalls:\n"
                  "      m_Calls: []\n"))

    # ---------------- UI ----------------
    canvas = root("Canvas", rect=dict(amin=(0, 0), amax=(0, 0), size=(0, 0),
                                      apos=(0, 0), pivot=(0, 0)))
    canvas.add(c_canvas())
    canvas.add(c_canvas_scaler(1280, 720, match=0.5))
    canvas.add(c_raycaster())

    # The EventSystem is what lets the mouse click the Restart button.
    event_system = root("EventSystem", pos=(0, 0, 0))
    event_system.add(c_event_system())
    event_system.add(c_standalone_input_module())

    # Score in the top-right corner: 24 px in, 16 px down, right-aligned text.
    score_go = rect("ScoreText", canvas, size=(520, 84), apos=(-24, -16),
                    pivot=(1, 1), amin=(1, 1), amax=(1, 1))
    score_go.add(c_canvas_renderer())
    score_go.add(c_text("Score: 0", font_size=48, align=2, style=1,
                        color_=(0.09, 0.13, 0.23, 1), raycast=False))

    # Best score, right under the score.
    best_go = rect("BestScoreText", canvas, size=(520, 56), apos=(-24, -100),
                   pivot=(1, 1), amin=(1, 1), amax=(1, 1))
    best_go.add(c_canvas_renderer())
    best_go.add(c_text("Best: 0", font_size=30, align=2, style=1,
                       color_=(0.09, 0.13, 0.23, 0.75), raycast=False))

    # Start hint, shown before the first tap.
    hint = rect("TapToStart", canvas, size=(1000, 110), apos=(0, 60),
                amin=(0.5, 0.5), amax=(0.5, 0.5))
    hint.add(c_canvas_renderer())
    hint.add(c_text("Click, Tap or Space to Start", font_size=56, align=4, style=1,
                    color_=(0.09, 0.13, 0.23, 1), raycast=False))

    # Game Over panel (hidden until the player crashes).
    panel = rect("GameOverPanel", canvas, size=(900, 520),
                 amin=(0.5, 0.5), amax=(0.5, 0.5))
    panel.active = False
    panel.add(c_canvas_renderer())
    panel.add(c_image(GUID["Assets/Art/Sprites/UIRoundedBox.png"],
                      (0.09, 0.12, 0.19, 0.88), image_type=1, raycast=True))  # 1 = Sliced

    title = rect("GameOverTitle", panel, size=(900, 120), apos=(0, 160),
                 amin=(0.5, 0.5), amax=(0.5, 0.5))
    title.add(c_canvas_renderer())
    title.add(c_text("GAME OVER", font_size=96, align=4, style=1,
                     color_=(1, 0.36, 0.32, 1), raycast=False))

    final = rect("FinalScoreText", panel, size=(900, 110), apos=(0, 30),
                 amin=(0.5, 0.5), amax=(0.5, 0.5))
    final.add(c_canvas_renderer())
    final_score = final.add(c_text("Score: 0", font_size=64, align=4, style=1,
                                   color_=(1, 1, 1, 1), raycast=False))

    button = rect("RestartButton", panel, size=(420, 130), apos=(0, -120),
                  amin=(0.5, 0.5), amax=(0.5, 0.5))
    button.add(c_canvas_renderer())
    btn_image = button.add(c_image(GUID["Assets/Art/Sprites/UIRoundedBox.png"],
                                   (0.25, 0.78, 0.45, 1), image_type=1, raycast=True))

    label = rect("Text", button, size=(420, 130), amin=(0, 0), amax=(1, 1))
    label.add(c_canvas_renderer())
    label.add(c_text("Restart", font_size=56, align=4, style=1,
                     color_=(1, 1, 1, 1), raycast=False))

    def onclick(target_path, method):
        target = by_path[target_path]
        return ("      - m_Target: {fileID: %d}\n"
                "        m_TargetAssemblyTypeName: GameManager, Assembly-CSharp\n"
                "        m_MethodName: %s\n"
                "        m_Mode: 1\n"
                "        m_Arguments:\n"
                "          m_ObjectArgument: {fileID: 0}\n"
                "          m_ObjectArgumentAssemblyTypeName: UnityEngine.Object, UnityEngine\n"
                "          m_IntArgument: 0\n"
                "          m_FloatArgument: 0\n"
                "          m_StringArgument: \n"
                "          m_BoolArgument: 0\n"
                "        m_CallState: 2\n" % (target.id, method))

    # ---------------------------------------------------------------
    # Assign fileIDs: walk the tree in a fixed order so IDs are stable.
    # ---------------------------------------------------------------
    def walk(o):
        yield o
        for c in o.children:
            for x in walk(c):
                yield x

    ordered = []
    for r in SCENE_OBJS:
        ordered.extend(walk(r))

    nid = 1000
    for o in ordered:
        by_path[o.path] = o
        o.id = nid
        nid += 1
        o.transform_id = nid
        nid += 1
        for c in o.comps:
            c[3] = nid
            nid += 1

    # Button needs the GameManager id, so it is created after the ids exist.
    button.add(c_button(button.comp_id(btn_image), onclick("GameManager", "RestartGame")))
    button.comps[-1][3] = nid
    nid += 1

    # ---------------------------------------------------------------
    # Fill in the cross references inside script bodies.
    # ---------------------------------------------------------------
    def go_ref(path):
        return "{fileID: %d}" % by_path[path].id

    def comp_ref(path, index):
        return "{fileID: %d}" % by_path[path].comp_id(index)

    def scene_refs(body):
        return (body.replace("__PREFAB__", "{fileID: %d, guid: %s, type: 3}"
                             % (PREFAB_ROOT_ID, GUID["Assets/Prefabs/Obstacle.prefab"]))
                    .replace("__PLAYER__", comp_ref("Player", 3))
                    .replace("__SPAWNER__", comp_ref("ObstacleSpawner", 0))
                    .replace("__SCORETEXT__", comp_ref("Canvas/ScoreText", 1))
                    .replace("__GAMEOVERPANEL__", go_ref("Canvas/GameOverPanel"))
                    .replace("__FINALSCORE__", comp_ref("Canvas/GameOverPanel/FinalScoreText", 1))
                    .replace("__TAPTOSTART__", go_ref("Canvas/TapToStart"))
                    .replace("__BESTSCORE__", comp_ref("Canvas/BestScoreText", 1)))

    # ---------------------------------------------------------------
    # Serialise
    # ---------------------------------------------------------------
    docs = []
    for index, o in enumerate(ordered):
        root_index = SCENE_OBJS.index(o) if o.parent is None else 0
        emit_object(o, root_index, docs)
    body = "".join(docs)
    body = scene_refs(body)

    roots = "".join("  - {fileID: %d}\n" % o.transform_id for o in SCENE_OBJS)
    text = (HEAD + scene_preamble() + body +
            "--- !u!1660057539 &9223372036854775807\nSceneRoots:\n"
            "  m_ObjectHideFlags: 0\n"
            "  m_Roots:\n" + roots)
    write("Assets/Scenes/Game.unity", text)


def scene_preamble():
    return """--- !u!29 &1
OcclusionCullingSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 2
  m_OcclusionBakeSettings:
    smallestOccluder: 5
    smallestHole: 0.25
    backfaceThreshold: 100
  m_SceneGUID: 00000000000000000000000000000000
  m_OcclusionCullingData: {fileID: 0}
--- !u!104 &2
RenderSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 9
  m_Fog: 0
  m_FogColor: {r: 0.5, g: 0.5, b: 0.5, a: 1}
  m_FogMode: 3
  m_FogDensity: 0.01
  m_LinearFogStart: 0
  m_LinearFogEnd: 300
  m_AmbientSkyColor: {r: 0.212, g: 0.227, b: 0.259, a: 1}
  m_AmbientEquatorColor: {r: 0.114, g: 0.125, b: 0.133, a: 1}
  m_AmbientGroundColor: {r: 0.047, g: 0.043, b: 0.035, a: 1}
  m_AmbientIntensity: 1
  m_AmbientMode: 3
  m_SubtractiveShadowColor: {r: 0.42, g: 0.478, b: 0.627, a: 1}
  m_SkyboxMaterial: {fileID: 0}
  m_HaloStrength: 0.5
  m_FlareStrength: 1
  m_FlareFadeSpeed: 3
  m_HaloTexture: {fileID: 0}
  m_SpotCookie: {fileID: 10001, guid: 0000000000000000e000000000000000, type: 0}
  m_DefaultReflectionMode: 0
  m_DefaultReflectionResolution: 128
  m_ReflectionBounces: 1
  m_ReflectionIntensity: 1
  m_CustomReflection: {fileID: 0}
  m_Sun: {fileID: 0}
  m_IndirectSpecularColor: {r: 0, g: 0, b: 0, a: 1}
  m_UseRadianceAmbientProbe: 0
--- !u!157 &3
LightmapSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 12
  m_GIWorkflowMode: 1
  m_GISettings:
    serializedVersion: 2
    m_BounceScale: 1
    m_IndirectOutputScale: 1
    m_AlbedoBoost: 1
    m_EnvironmentLightingMode: 0
    m_EnableBakedLightmaps: 0
    m_EnableRealtimeLightmaps: 0
  m_LightmapEditorSettings:
    serializedVersion: 12
    m_Resolution: 2
    m_BakeResolution: 40
    m_AtlasSize: 1024
    m_AO: 0
    m_AOMaxDistance: 1
    m_CompAOExponent: 1
    m_CompAOExponentDirect: 0
    m_ExtractAmbientOcclusion: 0
    m_Padding: 2
    m_LightmapParameters: {fileID: 0}
    m_LightmapsBakeMode: 1
    m_TextureCompression: 1
    m_FinalGather: 0
    m_FinalGatherFiltering: 1
    m_FinalGatherRayCount: 256
    m_ReflectionCompression: 2
    m_MixedBakeMode: 2
    m_BakeBackend: 1
    m_PVRSampling: 1
    m_PVRDirectSampleCount: 32
    m_PVRSampleCount: 512
    m_PVRBounces: 2
    m_PVREnvironmentSampleCount: 256
    m_PVREnvironmentReferencePointCount: 2048
    m_PVRFilteringMode: 1
    m_PVRDenoiserTypeDirect: 1
    m_PVRDenoiserTypeIndirect: 1
    m_PVRDenoiserTypeAO: 1
    m_PVRFilterTypeDirect: 0
    m_PVRFilterTypeIndirect: 0
    m_PVRFilterTypeAO: 0
    m_PVREnvironmentMIS: 1
    m_PVRCulling: 1
    m_PVRFilteringGaussRadiusDirect: 1
    m_PVRFilteringGaussRadiusIndirect: 5
    m_PVRFilteringGaussRadiusAO: 2
    m_PVRFilteringAtrousPositionSigmaDirect: 0.5
    m_PVRFilteringAtrousPositionSigmaIndirect: 2
    m_PVRFilteringAtrousPositionSigmaAO: 1
    m_ExportTrainingData: 0
    m_TrainingDataDestination: TrainingData
    m_LightProbeSampleCountMultiplier: 4
  m_LightingDataAsset: {fileID: 0}
  m_LightingSettings: {fileID: 0}
--- !u!196 &4
NavMeshSettings:
  serializedVersion: 2
  m_ObjectHideFlags: 0
  m_BuildSettings:
    serializedVersion: 2
    agentTypeID: 0
    agentRadius: 0.5
    agentHeight: 2
    agentSlope: 45
    agentClimb: 0.4
    ledgeDropHeight: 0
    maxJumpAcrossDistance: 0
    minRegionArea: 2
    manualCellSize: 0
    cellSize: 0.16666667
    manualTileSize: 0
    tileSize: 256
    accuratePlacement: 0
    maxJobWorkers: 0
    preserveTilesOutsideBounds: 0
    debug:
      m_Flags: 0
  m_NavMeshData: {fileID: 0}
"""


def emit_object(o, root_order, docs):
    comp_ids = [c[3] for c in o.comps]
    lines = [
        "--- !u!1 &%d\n" % o.id,
        "GameObject:\n",
        "  m_ObjectHideFlags: 0\n",
        "  m_CorrespondingSourceObject: {fileID: 0}\n",
        "  m_PrefabInstance: {fileID: 0}\n",
        "  m_PrefabAsset: {fileID: 0}\n",
        "  serializedVersion: 6\n",
        "  m_Component:\n",
        "  - component: {fileID: %d}\n" % o.transform_id,
    ]
    for cid in comp_ids:
        lines.append("  - component: {fileID: %d}\n" % cid)
    lines += [
        "  m_Layer: %d\n" % (5 if o.rect is not None else 0),
        "  m_Name: %s\n" % o.name,
        "  m_TagString: %s\n" % o.tag,
        "  m_Icon: {fileID: 0}\n",
        "  m_NavMeshLayer: 0\n",
        "  m_StaticEditorFlags: 0\n",
        "  m_IsActive: %d\n" % (1 if o.active else 0),
    ]
    docs.append("".join(lines))
    docs.append(emit_transform(o, root_order))
    for c in o.comps:
        body = c[2].replace("%GOID%", str(o.id))
        docs.append("--- !u!%s &%d\n%s:\n%s" % (c[0], c[3], c[1], body))


def emit_transform(o, root_order):
    head = ("--- !u!224 &%d\nRectTransform:\n" % o.transform_id if o.rect is not None
            else "--- !u!4 &%d\nTransform:\n" % o.transform_id)
    lines = [
        head,
        "  m_ObjectHideFlags: 0\n",
        "  m_CorrespondingSourceObject: {fileID: 0}\n",
        "  m_PrefabInstance: {fileID: 0}\n",
        "  m_PrefabAsset: {fileID: 0}\n",
        "  m_GameObject: {fileID: %d}\n" % o.id,
        "  m_LocalRotation: {x: 0, y: 0, z: 0, w: 1}\n",
        "  m_LocalPosition: {x: %s, y: %s, z: %s}\n" % tuple(fmt(v) for v in o.pos),
        "  m_LocalScale: {x: %s, y: %s, z: %s}\n" % tuple(fmt(v) for v in o.scale),
        "  m_ConstrainProportionsScale: 0\n",
    ]
    if o.children:
        lines.append("  m_Children:\n")
        for c in o.children:
            lines.append("  - {fileID: %d}\n" % c.transform_id)
    else:
        lines.append("  m_Children: []\n")
    lines.append("  m_Father: {fileID: %d}\n" % (o.parent.transform_id if o.parent else 0))
    if o.parent is None:
        lines.append("  m_RootOrder: %d\n" % root_order)
    if o.rect is not None:
        r = o.rect
        lines += [
            "  m_AnchorMin: {x: %s, y: %s}\n" % (fmt(r["amin"][0]), fmt(r["amin"][1])),
            "  m_AnchorMax: {x: %s, y: %s}\n" % (fmt(r["amax"][0]), fmt(r["amax"][1])),
            "  m_AnchoredPosition: {x: %s, y: %s}\n" % (fmt(r["apos"][0]), fmt(r["apos"][1])),
            "  m_SizeDelta: {x: %s, y: %s}\n" % (fmt(r["size"][0]), fmt(r["size"][1])),
            "  m_Pivot: {x: %s, y: %s}\n" % (fmt(r["pivot"][0]), fmt(r["pivot"][1])),
        ]
    lines.append("  m_LocalEulerAnglesHint: {x: 0, y: 0, z: 0}\n")
    return "".join(lines)


# ---------------------------------------------------------------------------
# Obstacle prefab
# ---------------------------------------------------------------------------
def build_prefab():
    guid = GUID["Assets/Prefabs/Obstacle.prefab"]
    # A prefab asset is referenced by the fileID of its ROOT GameObject, and Unity's
    # convention for that root is 100100000. Scene references (obstaclePrefab) must
    # use exactly this number, so it is defined once here and used in both places.
    go_id = 100100000
    tr_id = 100100001
    sr_id = 100100002
    col_id = 100100003
    mover_id = 100100004

    body = []
    body.append(
        "--- !u!1 &%d\nGameObject:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_CorrespondingSourceObject: {fileID: 0}\n"
        "  m_PrefabInstance: {fileID: 0}\n"
        "  m_PrefabAsset: {fileID: 0}\n"
        "  serializedVersion: 6\n"
        "  m_Component:\n"
        "  - component: {fileID: %d}\n"
        "  - component: {fileID: %d}\n"
        "  - component: {fileID: %d}\n"
        "  - component: {fileID: %d}\n"
        "  m_Layer: 0\n"
        "  m_Name: Obstacle\n"
        "  m_TagString: Obstacle\n"
        "  m_Icon: {fileID: 0}\n"
        "  m_NavMeshLayer: 0\n"
        "  m_StaticEditorFlags: 0\n"
        "  m_IsActive: 1\n"
        % (go_id, tr_id, sr_id, col_id, mover_id))
    body.append(
        "--- !u!4 &%d\nTransform:\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_CorrespondingSourceObject: {fileID: 0}\n"
        "  m_PrefabInstance: {fileID: 0}\n"
        "  m_PrefabAsset: {fileID: 0}\n"
        "  m_GameObject: {fileID: %d}\n"
        "  m_LocalRotation: {x: 0, y: 0, z: 0, w: 1}\n"
        "  m_LocalPosition: {x: 0, y: 0, z: 0}\n"
        "  m_LocalScale: {x: 1, y: 1, z: 1}\n"
        "  m_ConstrainProportionsScale: 0\n"
        "  m_Children: []\n"
        "  m_Father: {fileID: 0}\n"
        "  m_RootOrder: 0\n"
        "  m_LocalEulerAnglesHint: {x: 0, y: 0, z: 0}\n" % (tr_id, go_id))

    sprite = c_sprite(GUID["Assets/Art/Sprites/Obstacle.png"], (1, 1, 1, 1), order=5)
    collider = c_box_collider((1, 2))  # the sprite is 64x128 px at 100 px per unit
    mover = c_mono(GUID["Assets/Scripts/ObstacleMover.cs"],
                   "  speed: 4.5\n  passX: -7\n  destroyX: -14\n  scoreValue: 1\n")

    for class_id, type_name, text, fid in (
            (sprite[0], sprite[1], sprite[2], sr_id),
            (collider[0], collider[1], collider[2], col_id),
            (mover[0], mover[1], mover[2], mover_id)):
        body.append("--- !u!%s &%d\n%s:\n%s" % (class_id, fid, type_name,
                                                text.replace("%GOID%", str(go_id))))

    write("Assets/Prefabs/Obstacle.prefab", HEAD + "".join(body))


if __name__ == "__main__":
    write_metas()
    build_prefab()
    build_scene()
