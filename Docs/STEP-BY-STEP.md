# Build "Square Jumper" from scratch — Unity 2022.1 tutorial

This walks you from an **empty project** to the finished game in this repository.
Every step says **which menu to click**, **which file to create**, **which
GameObject gets the script**, and **which value to type into the Inspector**.

If you only want to *play* the finished game, stop here and press Play — the
project already contains everything. Use this document when you want to
understand it, or rebuild it yourself.

**Time needed:** about 60–90 minutes, no prior Unity experience required.

**What you end up with:** six short scripts, one prefab, one scene, and a player
that jumps, scores, crashes, shows Game Over and restarts — the exact contents of
this repository.

---

## The finished project at a glance

| File | Lines | Responsibility |
|---|---|---|
| `Assets/Scripts/PlayerController.cs` | 184 | read input, jump, detect the ground with a `Physics2D.Raycast` |
| `Assets/Scripts/ObstacleMover.cs` | 51 | slide one obstacle left, award a point when passed, delete it |
| `Assets/Scripts/ObstacleSpawner.cs` | 125 | spawn obstacles, ramp the difficulty |
| `Assets/Scripts/PlayerCollision.cs` | 40 | "I touched an Obstacle" → `GameManager.GameOver()` |
| `Assets/Scripts/GameManager.cs` | 250 | score, start, game over, best score, restart, UI text |
| `Assets/Scripts/BackgroundScroller.cs` | 37 | optional moving clouds |
| `Assets/Prefabs/Obstacle.prefab` | — | Sprite + BoxCollider2D + ObstacleMover, tag `Obstacle` |
| `Assets/Scenes/Game.unity` | — | camera, ground, player, spawner, Canvas, EventSystem |

---

## Contents

1. [Create the 2D project](#step-1--create-the-2d-project)
2. [Set up the scene](#step-2--set-up-the-game-scene-camera--ground)
3. [Create the player](#step-3--create-the-player)
4. [Jumping](#step-4--make-the-player-jump)
5. [Obstacles + spawning](#step-5--create-the-obstacle-prefab-and-the-spawner)
6. [Collision detection](#step-6--collision-detection--game-over)
7. [Scoring + HUD](#step-7--scoring-and-the-hud)
8. [Game Over + Restart UI](#step-8--the-game-over-panel-and-restart-button)
9. [Polish](#step-9--polish-background-and-difficulty)
10. [Recap and next steps](#step-10--recap)

---

## Step 1 — Create the 2D project

1. Open **Unity Hub** → **New project**.
2. Select the **2D Core** template (in Unity 2022.1 it is simply called
   **2D**). If you see **2D (URP)**, do **not** pick it — this game uses the
   built-in pipeline, which is simpler and needs no extra packages.
3. **Unity Editor Version:** 2022.1.x.
4. **Project name:** `Square Jumper`. **Location:** anywhere outside this repo.
5. **Create project** and wait for the editor to open.

**Check that 2D mode is on:** **Edit → Project Settings → Editor** →
*Default Behavior Mode* = **2D**. In 2D mode the Scene view is a flat
front view and new images import as Sprites automatically.

> **Already have this repository?** You can skip to Step 2 and use the existing
> assets. Everything below also works in a fresh project, where you create the
> sprites yourself (Step 2.1 shows how to make a quick one).

### Good to know before you start

* **Scene view** = where you place things. **Game view** = what the player sees.
* The **Inspector** (right side) shows the components of whatever you selected.
* **Play** (▶) runs the game. Any change you make while playing is undone when
  you stop — use that to experiment safely.

---

## Step 2 — Set up the game scene (camera + ground)

### 2.1 Get some sprites (2 minutes)

Use the ready-made images in `Assets/Art/Sprites/`, or make your own.

| File | Size (px) | Imported size (units at 100 PPU) | Used for |
|---|---|---|---|
| `Player.png` | 64 × 64 | 1 × 1 | the character |
| `Obstacle.png` | 64 × 128 | 1 × 2 | the obstacle prefab |
| `Ground.png` | 64 × 64 | tile, Draw Mode **Tiled** | dirt fill |
| `GroundGrass.png` | 64 × 24 | tile | the green grass line |
| `Cloud.png` | 128 × 64 | 1.28 × 0.64 | decoration |
| `SkyGradient.png` | 8 × 256 | **Pixels Per Unit = 1** | sky background |
| `UIRoundedBox.png` | 32 × 32 | UI sprite, border 10 | Game Over panel + button |

Every sprite in this repo uses **Sprite Mode = Single**, **Pixels Per Unit = 100**
(except the sky, which uses 1), **Filter Mode = Bilinear**, **Compression = None**
and **Wrap Mode = Clamp** (Ground, GroundGrass and the sky use **Repeat** so they
tile seamlessly). Those settings are inside each `.png.meta` file, which is why
the game looks the same on your machine as on the author's.

To make your own instead:

* **Right-click** in the Project window → **Create → 2D → Sprites → Square**.
* Anything you import (drag a PNG into the Project window) will be a Sprite if
  2D mode is on. Select it and make sure the Inspector shows
  **Texture Type = Sprite (2D and UI)** and **Pixels Per Unit = 100**.

With 100 pixels per unit, a **64 × 64** image becomes exactly **1 × 1 world
unit**. That makes all the numbers below easy: the player is 1 × 1, the
obstacle is 1 × 2.

### 2.2 Set up the camera

1. In the **Hierarchy**, select **Main Camera**.
2. Inspector → **Camera**:
   * **Projection:** Orthographic (2D is always orthographic)
   * **Size:** `6`  → the view is 12 units tall, about 21 units wide at 16:9
   * **Position:** `(0, 0, -10)`
   * **Clear Flags:** Solid Color, **Background:** a light blue (e.g. `#9ED4FA`)
3. Game view: set the aspect dropdown (top-left of the Game view) to
   **16:9** so what you see matches a normal screen.

### 2.3 Create the ground

1. **GameObject → 2D Object → Sprites → Square** (or drag your `Ground.png`
   into the Hierarchy). Rename it **Ground**.
2. Inspector:
   * **Sprite Renderer → Sprite:** `Ground.png`
   * **Draw Mode:** **Tiled** (the texture repeats instead of stretching),
     **Size:** `X 60`, `Y 12`
   * **Order in Layer:** `-10` (so it draws behind everything else)
   * **Transform → Position:** `(0, -8, 0)`
3. **Add Component → Box Collider 2D**, then set:
   * **Size:** `X 60`, `Y 12`
   * **Offset:** `0, 0`

Why these numbers? The collider is 12 units tall and centred at y = -8, so its
**top edge sits at y = -2**. That is the floor the player lands on, and it is
visible just below the middle of the screen.

4. Optional but recommended: duplicate the ground idea for the **grass strip**.
   Create another Sprite object called **GroundGrass** with `GroundGrass.png`,
   Draw Mode **Tiled**, Size `60 × 0.24`, position `(0, -2, -0.5)`,
   Order in Layer `-9`. No collider needed.

### 2.4 Save the scene

**File → Save As…** → `Assets/Scenes/Game.unity`.

> Tip: with the scene saved, press **Ctrl/Cmd + S** often. Unity does not
> autosave scene changes.

---

## Step 3 — Create the player

### 3.1 The GameObject

1. **GameObject → 2D Object → Sprites → Square** → rename it **Player**.
2. **Transform:**
   * **Position:** `(-6, -1.5, 0)`  (the bottom lands exactly on the ground)
   * **Scale:** `1, 1, 1`
3. **Sprite Renderer:** Sprite = `Player.png`, **Order in Layer** = `10`.
4. **Tag:** at the top of the Inspector set the tag to **Player**
   (it already exists in Unity; if not, *Add Tag…* → `Player`).

### 3.2 Physics components

**Add Component → Box Collider 2D** → **Size** `1, 1`, **Offset** `0, 0`.

**Add Component → Rigidbody 2D** and set:

| Field | Value | Why |
|---|---|---|
| Body Type | **Dynamic** | it must be pushed by gravity |
| Mass | `1` | doesn't matter much here |
| Gravity Scale | `2.2` | a snappier arcade fall than the default 1 |
| Collision Detection | **Continuous** | no tunnelling when the game speeds up |
| Interpolate | **Interpolate** | smooth motion between physics steps |
| Constraints → Freeze Rotation → **Z** | ✔ on | a bump must never spin the player |

> **Why Dynamic and not Kinematic?** A Kinematic body ignores gravity and
> collisions. We want a real jump arc and a real crash, so the player has to be
> Dynamic. (The obstacles, in contrast, are plain colliders without a
> Rigidbody 2D — Unity treats those as immovable, which is exactly right.)

### 3.3 Create the script

1. In the **Project** window, **right-click `Assets/Scripts` → Create → C#
   Script**, name it **`PlayerController`**. Folders: if `Assets/Scripts` does
   not exist yet, create it first (**right-click `Assets` → Create → Folder**).
   Keeping scripts in a `Scripts` folder is a habit worth having.
2. **Double-click** the script to open it in your IDE (Visual Studio / Rider /
   VS Code) and replace the whole file with the code below.
3. Save, then go back to Unity (it recompiles automatically; a spinner appears
   in the bottom-right corner).

`Assets/Scripts/PlayerController.cs`:

```csharp
using UnityEngine;

/// <summary>
/// Lets the player jump. The player stays on its spot and the obstacles come towards it,
/// which keeps the camera still and the game easy to follow.
///
/// Attach to the Player GameObject. That GameObject also needs:
///   - a Sprite Renderer (the square character)
///   - a Box Collider 2D (size 1 x 1)
///   - a Rigidbody 2D (Dynamic body, Gravity Scale 2.2, Freeze Rotation Z = on)
/// </summary>
public class PlayerController : MonoBehaviour
{
    [Header("Jump")]
    [Tooltip("How hard the player pushes off the ground. Bigger number = higher jump.")]
    public float jumpForce = 12f;

    [Tooltip("How far below the feet to look for the ground. 0.1 is plenty.")]
    public float groundCheckDistance = 0.12f;

    [Tooltip("Which layers count as solid ground. 'Everything' is fine to start with.")]
    public LayerMask groundLayers = ~0;

    [Header("Input")]
    [Tooltip("Left mouse button or a tap on a touch screen makes the player jump.")]
    public bool useMouseAndTouch = true;

    [Tooltip("The space bar also makes the player jump.")]
    public bool useSpaceBar = true;

    // Set up in Awake().
    private Rigidbody2D rb;
    private Collider2D col;

    // The game manager keeps the player frozen until the game starts.
    private bool isFrozen = true;

    // On a crash the player keeps falling (it looks natural) but can no longer jump.
    private bool inputEnabled = true;

    // Input is read in Update() but applied in FixedUpdate(), so a click is never lost.
    private bool jumpRequested;

    private bool isGrounded;

    /// <summary>True while the player is standing on something. Handy for debugging.</summary>
    public bool IsGrounded { get { return isGrounded; } }

    private void Awake()
    {
        rb = GetComponent<Rigidbody2D>();
        col = GetComponent<Collider2D>();

        if (rb == null)
        {
            Debug.LogError("PlayerController needs a Rigidbody2D on the same GameObject.", this);
            return;
        }

        // The player must fall and land, so it has to be a Dynamic body.
        rb.bodyType = RigidbodyType2D.Dynamic;

        // Never let a bump spin the player.
        rb.freezeRotation = true;

        // If you forget to set it in the Inspector, make sure gravity pulls the player down.
        if (rb.gravityScale < 0.1f)
        {
            rb.gravityScale = 2.2f;
        }
    }

    private void Update()
    {
        if (isFrozen)
        {
            return;
        }

        if (!inputEnabled)
        {
            isGrounded = CheckForGround();
            return;
        }

        // 1. Are we standing on the ground? Checked every frame so jumps feel instant.
        isGrounded = CheckForGround();

        // 2. Remember the input.
        if (JumpWasPressed())
        {
            jumpRequested = true;
        }
    }

    private void FixedUpdate()
    {
        if (rb == null)
        {
            return;
        }

        if (isFrozen)
        {
            // Hold still, but still let gravity settle the player onto the ground.
            rb.velocity = new Vector2(0f, rb.velocity.y);
            return;
        }

        if (jumpRequested)
        {
            jumpRequested = false;

            // Only jump when actually touching the ground (no double jumps).
            if (isGrounded)
            {
                rb.velocity = new Vector2(rb.velocity.x, jumpForce);
            }
        }
    }

    /// <summary>
    /// Shoots a very short ray straight down from just underneath the player's collider.
    /// If it hits something, the player is standing on it.
    /// </summary>
    private bool CheckForGround()
    {
        if (col == null)
        {
            return false;
        }

        // Start slightly BELOW the collider, so the ray can never hit the player itself.
        Vector2 origin = new Vector2(col.bounds.center.x, col.bounds.min.y - 0.02f);
        RaycastHit2D hit = Physics2D.Raycast(origin, Vector2.down, groundCheckDistance, groundLayers);

        return hit.collider != null && hit.collider != col;
    }

    private bool JumpWasPressed()
    {
        if (useSpaceBar && Input.GetKeyDown(KeyCode.Space))
        {
            return true;
        }

        if (useMouseAndTouch && Input.GetMouseButtonDown(0))
        {
            return true;
        }

        return false;
    }

    /// <summary>Called by GameManager: true = wait for the player, false = let them move.</summary>
    public void SetFrozen(bool frozen)
    {
        isFrozen = frozen;

        if (frozen)
        {
            inputEnabled = true;    // ready for the next round
        }

        if (rb != null)
        {
            rb.velocity = Vector2.zero;
        }
    }

    /// <summary>
    /// Called by GameManager on a crash: the player stops accepting jumps but keeps
    /// falling, so it lands on the ground instead of hanging in mid-air.
    /// </summary>
    public void SetInputEnabled(bool enabled)
    {
        inputEnabled = enabled;

        if (!enabled)
        {
            jumpRequested = false;
        }
    }
}
```

### 3.4 Attach it

1. Select **Player** in the Hierarchy → **Add Component** → type
   `PlayerController` → Enter. (Unity finds your new script by name.)
2. The Inspector now shows the script with the fields you declared:
   * **Jump Force** `12`
   * **Ground Check Distance** `0.12`
   * **Ground Layers** = `Everything`
   * **Use Mouse And Touch** ✔, **Use Space Bar** ✔

> If the fields do not appear, Unity has a compile error — look at the console
> (bottom of the editor, **Console** tab) and fix the red message first. A
> script with an error cannot be attached.

---

## Step 4 — Make the player jump

You already wrote the jumping code in Step 3.3. This section explains *why* it
is written that way, and how to test it before the game logic exists.

### The two-update rule

Unity runs **`Update()` every frame** (input, visuals) and
**`FixedUpdate()` at a fixed 50 times per second** (physics). Reading input in
`Update` and applying forces in `FixedUpdate` means a fast click is never lost.
That is what the `jumpRequested` flag is for.

### Ground detection with a raycast

`CheckForGround()` fires an invisible ray from just under the player's feet,
straight down, 0.12 units long. If it hits a collider, the player is standing on
something. This is more forgiving than `OnCollisionStay2D`, and it never
"sticks" to walls.

Start the ray at `bounds.min.y - 0.02f` — *below* the box — otherwise the ray
starts inside the player's own collider and reports the player as its own
ground.

### Test the jump on its own

`PlayerController` starts with `isFrozen = true`, so nothing moves until the
`GameManager` (Step 7) unfreezes it. To try the jump right now, unlock it
temporarily:

1. Add these two lines to `PlayerController`, right after `Awake()`:
   ```csharp
   private void Start()
   {
       SetFrozen(false);      // TEMPORARY: lets you test the jump before Step 7
   }
   ```
2. Press **Play** and click / press Space: the player hops, falls back, and lands
   with its feet exactly on the grass line.
3. **Delete the temporary `Start()` method** afterwards — the `GameManager`
   unfreezes the player properly once it exists.

Meanwhile you can already tune the feel: raise **Jump Force** for a bigger hop,
raise **Gravity Scale** on the Rigidbody 2D for a faster, heavier fall.

> **Verified numbers:** with `Jump Force = 12` and `Gravity Scale = 2.2`, the
> jump peak is **3.34 units** and the player is in the air for **1.11 s**. Step 5
> keeps every obstacle below that height, so every obstacle is always clearable.

---

## Step 5 — Create the Obstacle prefab and the spawner

### 5.1 The obstacle prefab

1. **GameObject → 2D Object → Sprites → Square** → rename it **Obstacle**.
2. **Transform:** Position `(0, 0, 0)`, Scale `1, 1, 1` (the spawner moves it).
3. **Sprite Renderer:** `Obstacle.png`, **Order in Layer** `5`.
   The image is 64 × 128 px, so at 100 PPU it is **1 × 2 units** on screen — no
   scaling needed.
4. **Add Component → Box Collider 2D** → **Size** `X 1`, `Y 2`, **Offset** `0, 0`.
   **No Rigidbody 2D**: a collider without a rigidbody is a static collider,
   which is what a wall should be.
5. **Tag → Add Tag…** → create `Obstacle` (one time only), then set the
   prefab's tag to **Obstacle**. This tag is how the player recognises a crash.

### 5.2 Move it (script)

Create `Assets/Scripts/ObstacleMover.cs`:

```csharp
using UnityEngine;

/// <summary>
/// Moves one obstacle to the left and deletes it once it is off screen.
/// When the obstacle has safely passed the player, it gives the GameManager a point.
///
/// Attach to the Obstacle prefab root (Assets/Prefabs/Obstacle.prefab).
/// The ObstacleSpawner sets the speed every time it spawns one.
/// </summary>
public class ObstacleMover : MonoBehaviour
{
    [Tooltip("How fast this obstacle moves left. The spawner overwrites this at runtime.")]
    public float speed = 4.5f;

    [Tooltip("X position where the obstacle is considered passed: the player gets a point here.")]
    public float passX = -7f;

    [Tooltip("X position where the obstacle is deleted so the scene stays clean.")]
    public float destroyX = -14f;

    [Tooltip("Points awarded for passing this obstacle.")]
    public int scoreValue = 1;

    private bool hasBeenCounted;

    private void Update()
    {
        transform.position += Vector3.left * speed * Time.deltaTime;

        // The obstacle is now behind the player: that is one successful pass.
        if (!hasBeenCounted && transform.position.x < passX)
        {
            hasBeenCounted = true;

            if (GameManager.Instance != null)
            {
                GameManager.Instance.AddScore(scoreValue);
            }
        }

        if (transform.position.x < destroyX)
        {
            Destroy(gameObject);
        }
    }

    public void SetSpeed(float newSpeed)
    {
        speed = newSpeed;
    }
}
```

`GameManager.Instance` does not exist yet — that is fine, C# compiles the file
only when the class exists. Do **Step 7 first** if you prefer to avoid the
temporary compile error, or create the file now and ignore the error until then.

Attach **ObstacleMover** to the **Obstacle** object (Add Component). Inspector:

* **Speed** `4.5` (the spawner overwrites this every time it spawns)
* **Pass X** `-7`, **Destroy X** `-14`, **Score Value** `1`

### 5.3 Turn it into a prefab

Drag **Obstacle** from the **Hierarchy** into `Assets/Prefabs` in the
**Project** window. A blue cube icon appears — that is the prefab.
Now delete the Obstacle from the Hierarchy: the spawner will create copies.

> **Why a prefab?** `Instantiate(prefab)` needs an asset, and changes made to a
> prefab apply to every copy. Editing the prefab later is a single click.

### 5.4 The spawner

1. **GameObject → Create Empty** → rename it **ObstacleSpawner**.
2. **Transform:** `(0, 0, 0)`.
3. Create `Assets/Scripts/ObstacleSpawner.cs`:

```csharp
using UnityEngine;

/// <summary>
/// Spawns obstacles off the right edge of the screen at a random height,
/// and slowly makes the game harder by speeding up and shortening the gap.
///
/// Attach to an empty GameObject called "ObstacleSpawner" and drag the
/// Assets/Prefabs/Obstacle prefab into the Obstacle Prefab slot.
/// </summary>
public class ObstacleSpawner : MonoBehaviour
{
    [Header("What to spawn")]
    [Tooltip("The Obstacle prefab. Drag Assets/Prefabs/Obstacle into this slot.")]
    public GameObject obstaclePrefab;

    [Header("Where")]
    [Tooltip("X position the obstacles appear at (just off screen to the right).")]
    public float spawnX = 11f;

    [Tooltip("Lowest y position an obstacle may appear at. The ground surface is y = -2, so -1.4 puts the bottom of the obstacle on the ground.")]
    public float minY = -1.4f;

    [Tooltip("Highest y position an obstacle may appear at. The player can clear up to y = 1.1, so do not go much higher than -0.4.")]
    public float maxY = -0.4f;

    [Header("Timing")]
    [Tooltip("Seconds between obstacles at the very start.")]
    public float startSpawnInterval = 1.7f;

    [Tooltip("The shortest gap the game will ever reach.")]
    public float minSpawnInterval = 0.85f;

    [Tooltip("How much the gap shrinks per second of play.")]
    public float intervalStepPerSecond = 0.02f;

    [Header("Speed")]
    [Tooltip("Obstacle speed at the very start.")]
    public float startSpeed = 4.5f;

    [Tooltip("How much faster the obstacles get per second of play.")]
    public float speedIncreasePerSecond = 0.3f;

    [Tooltip("The fastest the obstacles will ever move.")]
    public float maxSpeed = 15f;

    // Runtime values.
    private float timer;
    private float currentInterval;
    private float currentSpeed;
    private bool isSpawning;

    private void Start()
    {
        ResetDifficulty();
    }

    /// <summary>Puts speed and gap back to their starting values.</summary>
    public void ResetDifficulty()
    {
        timer = 0f;
        currentInterval = startSpawnInterval;
        currentSpeed = startSpeed;
        isSpawning = false;
    }

    /// <summary>Called by GameManager.StartGame.</summary>
    public void StartSpawning()
    {
        ResetDifficulty();
        isSpawning = true;

        // Small breather before the first obstacle so the player can find the controls.
        timer = 0.6f;
    }

    /// <summary>Called by GameManager.GameOver.</summary>
    public void StopSpawning()
    {
        isSpawning = false;
    }

    private void Update()
    {
        if (!isSpawning)
        {
            return;
        }

        if (obstaclePrefab == null)
        {
            Debug.LogWarning("ObstacleSpawner has no Obstacle Prefab assigned.", this);
            isSpawning = false;
            return;
        }

        // Slowly get harder.
        currentSpeed = Mathf.Min(currentSpeed + speedIncreasePerSecond * Time.deltaTime, maxSpeed);
        currentInterval = Mathf.Max(currentInterval - intervalStepPerSecond * Time.deltaTime,
                                    minSpawnInterval);

        timer += Time.deltaTime;
        if (timer >= currentInterval)
        {
            timer = 0f;
            SpawnOne();
        }
    }

    private void SpawnOne()
    {
        float randomY = Random.Range(minY, maxY);
        Vector3 spawnPosition = new Vector3(spawnX, randomY, 0f);

        GameObject obstacle = Instantiate(obstaclePrefab, spawnPosition, Quaternion.identity);

        ObstacleMover mover = obstacle.GetComponent<ObstacleMover>();
        if (mover != null)
        {
            mover.SetSpeed(currentSpeed);
        }
    }

    /// <summary>Current obstacle speed, handy for a HUD or for debugging.</summary>
    public float CurrentSpeed { get { return currentSpeed; } }
}
```

4. Attach it to **ObstacleSpawner**, then **drag `Assets/Prefabs/Obstacle.prefab` onto
   the `Obstacle Prefab` slot** in the Inspector.
5. Check the other fields against the defaults above.

### How the difficulty numbers were chosen

| Obstacle centre Y | Bottom / top edge | Player bottom at jump peak | Result |
|---|---|---|---|
| `-1.4` | -2.40 / -0.40 | 2.34 | easily cleared |
| `-0.9` | -1.90 / 0.10 | 2.34 | easily cleared |
| `-0.4` (highest) | -1.40 / 0.60 | 2.34 | cleared with 1.7 units to spare |

The player's jump peak puts the bottom of the player at **y = 2.34**, and the
highest obstacle top is **y = 0.60** — so the game is always fair, however fast
it gets. If you raise `maxY`, raise `jumpForce` as well.

---

## Step 6 — Collision detection & Game Over

The player has a Dynamic Rigidbody 2D; the obstacles are static colliders. Unity
calls `OnCollisionEnter2D` on the player when they touch. That is the whole
collision system — no code needed to detect the overlap, only to react to it.

Create `Assets/Scripts/PlayerCollision.cs` and attach it to the **Player**:

```csharp
using UnityEngine;

/// <summary>
/// Attach to the Player GameObject.
/// When the player touches anything with the "Obstacle" tag, the game is over.
///
/// The obstacles have no Rigidbody 2D, so they are static colliders. Unity still raises
/// OnCollisionEnter2D when the player's Dynamic Rigidbody2D runs into them, which is all
/// this script needs. OnTriggerEnter2D is handled too, in case you make the obstacle
/// collider a trigger later.
/// </summary>
[RequireComponent(typeof(Collider2D))]
public class PlayerCollision : MonoBehaviour
{
    [Tooltip("Tag that counts as a deadly obstacle. Create it once in Edit > Project Settings > Tags and Layers.")]
    public string obstacleTag = "Obstacle";

    private void OnCollisionEnter2D(Collision2D collision)
    {
        TryGameOver(collision.gameObject);
    }

    private void OnTriggerEnter2D(Collider2D other)
    {
        TryGameOver(other.gameObject);
    }

    private void TryGameOver(GameObject other)
    {
        if (!other.CompareTag(obstacleTag))
        {
            return;
        }

        if (GameManager.Instance != null)
        {
            GameManager.Instance.GameOver();
        }
    }
}
```

Inspector: **Obstacle Tag** = `Obstacle` (must be spelled exactly like the tag).

* `OnCollisionEnter2D` fires when solid colliders hit each other (our case).
* `OnTriggerEnter2D` is there in case you later tick **Is Trigger** on the
  obstacle collider.
* `CompareTag` is the fast, allocation-free way to compare tags — prefer it over
  `other.tag == "Obstacle"`.

> If the game does not end on contact: the player must have a **Rigidbody 2D**
> (Dynamic) for collision messages to be sent, and the tag must match exactly.

---

## Step 7 — Scoring and the HUD

### 7.1 The GameManager

Create `Assets/Scripts/GameManager.cs`:

```csharp
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.UI;

/// <summary>
/// The brain of the game: keeps the score, starts and ends the game, shows the UI.
/// There is only one GameManager in the scene and every other script reaches it
/// through GameManager.Instance, which is why you never have to drag references
/// between Prefabs.
///
/// Attach to an empty GameObject called "GameManager".
/// </summary>
public class GameManager : MonoBehaviour
{
    /// <summary>Anything can call GameManager.Instance from anywhere.</summary>
    public static GameManager Instance { get; private set; }

    [Header("Scene links")]
    [Tooltip("The Player object with PlayerController on it.")]
    public PlayerController player;

    [Tooltip("The ObstacleSpawner object.")]
    public ObstacleSpawner spawner;

    [Tooltip("Text that shows the score while playing.")]
    public Text scoreText;

    [Tooltip("Panel that appears on Game Over (Canvas > GameOverPanel).")]
    public GameObject gameOverPanel;

    [Tooltip("Text on that panel showing the final score.")]
    public Text finalScoreText;

    [Tooltip("Optional 'click to start' hint shown before the first jump.")]
    public GameObject tapToStartText;

    [Tooltip("Optional best score text. Leave empty if you do not want one.")]
    public Text bestScoreText;

    [Header("Events")]
    [Tooltip("Fires on Game Over. Hook up sounds or particle effects here, no code needed.")]
    public UnityEvent onGameOver;

    private int score;
    private bool isPlaying;
    private bool gameIsOver;

    public int Score { get { return score; } }
    public bool IsPlaying { get { return isPlaying; } }
    public bool IsGameOver { get { return gameIsOver; } }

    private void Awake()
    {
        // Only one GameManager may exist.
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }

        Instance = this;
    }

    private void OnDestroy()
    {
        if (Instance == this)
        {
            Instance = null;
        }
    }

    private void Start()
    {
        ShowStartScreen();
    }

    // ------------------------------------------------------------------
    // Game flow
    // ------------------------------------------------------------------

    /// <summary>The state before the first click: player frozen, no obstacles, hint visible.</summary>
    private void ShowStartScreen()
    {
        isPlaying = false;
        gameIsOver = false;
        score = 0;

        UpdateScoreText();

        if (gameOverPanel != null)
        {
            gameOverPanel.SetActive(false);
        }

        if (tapToStartText != null)
        {
            tapToStartText.SetActive(true);
        }

        if (spawner != null)
        {
            spawner.ResetDifficulty();
        }

        if (player != null)
        {
            player.SetFrozen(true);
        }

        ShowBestScore();
    }

    /// <summary>Starts a fresh round. Hooked up to the Restart button and to the first click.</summary>
    public void StartGame()
    {
        score = 0;
        isPlaying = true;
        gameIsOver = false;

        UpdateScoreText();

        if (gameOverPanel != null)
        {
            gameOverPanel.SetActive(false);
        }

        if (tapToStartText != null)
        {
            tapToStartText.SetActive(false);
        }

        if (player != null)
        {
            player.SetFrozen(false);
        }

        if (spawner != null)
        {
            spawner.StartSpawning();
        }
    }

    /// <summary>Called by PlayerCollision when the player hits an obstacle.</summary>
    public void GameOver()
    {
        if (!isPlaying)
        {
            return; // ignore the extra collision callbacks from the same crash
        }

        isPlaying = false;
        gameIsOver = true;

        if (spawner != null)
        {
            spawner.StopSpawning();
        }

        if (player != null)
        {
            player.SetInputEnabled(false);   // stop jumping, but let the player fall and land
        }

        if (finalScoreText != null)
        {
            finalScoreText.text = "Score: " + score;
        }

        if (gameOverPanel != null)
        {
            gameOverPanel.SetActive(true);
        }

        SaveBestScore();

        if (onGameOver != null)
        {
            onGameOver.Invoke();
        }
    }

    /// <summary>Restart button. Reloads the scene so nothing is left over.</summary>
    public void RestartGame()
    {
        UnityEngine.SceneManagement.SceneManager.LoadScene(
            UnityEngine.SceneManagement.SceneManager.GetActiveScene().buildIndex);
    }

    // ------------------------------------------------------------------
    // Score
    // ------------------------------------------------------------------

    /// <summary>Called by ObstacleMover once an obstacle is safely behind the player.</summary>
    public void AddScore(int amount)
    {
        if (!isPlaying)
        {
            return;
        }

        score += amount;
        UpdateScoreText();
    }

    private void Update()
    {
        // Click or press Space on the start screen to begin.
        if (isPlaying || gameIsOver)
        {
            return;
        }

        if (Input.GetMouseButtonDown(0) || Input.GetKeyDown(KeyCode.Space))
        {
            StartGame();
        }
    }

    private void UpdateScoreText()
    {
        if (scoreText != null)
        {
            scoreText.text = "Score: " + score;
        }
    }

    // ------------------------------------------------------------------
    // Best score, kept between sessions with PlayerPrefs. Optional but nice.
    // ------------------------------------------------------------------

    private void SaveBestScore()
    {
        int best = PlayerPrefs.GetInt("BestScore", 0);
        if (score > best)
        {
            PlayerPrefs.SetInt("BestScore", score);
            PlayerPrefs.Save();
        }

        ShowBestScore();
    }

    private void ShowBestScore()
    {
        if (bestScoreText != null)
        {
            bestScoreText.text = "Best: " + PlayerPrefs.GetInt("BestScore", 0);
        }
    }
}
```

**Attach it:** **GameObject → Create Empty** → name it **GameManager** →
Add Component → `GameManager`.

### 7.2 The Canvas and the score text

1. **GameObject → UI → Text**. Unity creates a **Canvas**, an **EventSystem**
   and a **Text** object. (If you only see the Text, add
   **GameObject → UI → Event System** — the Restart button later needs it.)
2. Select **Canvas** → Inspector → **Canvas Scaler**:
   * **UI Scale Mode:** Scale With Screen Size
   * **Reference Resolution:** `1280 × 720`
   * **Match:** `0.5`
   This keeps the UI the same size relative to the screen on every monitor.
3. Select the **Text** object, rename it **ScoreText**:
   * **Text:** `Score: 0`
   * **Font Size:** `48`, **Font Style:** Bold, **Alignment:** right + middle
   * **Color:** dark navy `#17213B` (reads well on the light sky)
   * **Rect Transform (anchor preset, top-right — the square icon in the
     Rect Transform header):** → **Anchor:** top-right, **Pivot:** `1, 1`,
     **Pos X** `-24`, **Pos Y** `-16`, **Width** `520`, **Height** `84`
4. Duplicate it (**Ctrl/Cmd + D**) → rename **BestScoreText**:
   * **Text:** `Best: 0`, **Font Size** `30`
   * **Pos Y** `-100`, **Height** `56`
5. Duplicate again → **TapToStart**:
   * **Text:** `Click, Tap or Space to Start`, **Font Size** `56`,
     **Alignment:** centre/middle
   * **Anchor:** centre, **Pos** `0, 60`, **Width** `1000`, **Height** `110`

> **Text is invisible?** Expand the Text component's **Font** slot and pick
> `LegacyRuntime.ttf` (Unity 2022) or `Arial.ttf` (older versions). Legacy UI
> Text does not ship with a font assigned in every template.

### 7.3 Wire the references

Select **GameManager** and drag into its Inspector slots:

| Slot | Drag this |
|---|---|
| Player | **Player** (Hierarchy) |
| Spawner | **ObstacleSpawner** (Hierarchy) |
| Score Text | **ScoreText** (Hierarchy) |
| Best Score Text | **BestScoreText** |
| Tap To Start Text | **TapToStart** |
| Game Over Panel | leave empty until Step 8 |
| Final Score Text | leave empty until Step 8 |

Press **Play**: the hint shows, clicking starts the run, obstacles appear, and
the score goes up each time one passes. Hitting one does nothing yet — the panel
does not exist.

> **Why `GameManager.Instance`?** The spawned obstacles are prefabs created at
> runtime; they cannot have a reference dragged onto them in the editor. A
> static `Instance` property gives every script a one-line way to reach the
> manager, whatever its name or position.

---

## Step 8 — The Game Over panel and Restart button

### 8.1 The panel

1. Right-click **Canvas** → **UI → Image** → rename it **GameOverPanel**.
2. Rect Transform: **Anchor** centre, **Pos** `0, 0`, **Width** `900`,
   **Height** `520`.
3. **Image** component:
   * **Source Image:** `UIRoundedBox` (or `UI/Skin/UISprite.psd` if you have
     the default UI sprites; `UIRoundedBox.png` is a 32 × 32 rounded square with
     a 10 px border, so set **Image Type = Sliced** and it scales without
     distorting)
   * **Color:** dark navy, alpha ≈ `0.9`
4. Un-tick the panel's **active checkbox** at the top-left of the Inspector (or
   `GameObject → Set Active` off). The `GameManager` shows it on Game Over.

### 8.2 The texts

Right-click **GameOverPanel** → **UI → Text** twice:

| Object | Text | Font size | Position (anchored centre) |
|---|---|---|---|
| **GameOverTitle** | `GAME OVER` | 96, Bold | `0, 160` |
| **FinalScoreText** | `Score: 0` | 64, Bold | `0, 30` |

Colour the title a warm red (`#FF5C52`), the score white. Width `900`,
Height `120` / `110`.

### 8.3 The Restart button

1. Right-click **GameOverPanel** → **UI → Button** → rename **RestartButton**.
2. Rect Transform: centre anchor, **Pos** `0, -120`, **Width** `520`,
   **Height** `140`.
3. On the **Image** part of the button set **Source Image** = `UIRoundedBox`,
   **Image Type** = Sliced, **Color** = green `#40C773`.
4. Select its child **Text**: change the text to `Restart`, **Font Size** `56`,
   colour white.
5. With **RestartButton** selected, scroll to the **Button** component →
   **On Click ()** → **+** → drag the **GameManager** object into the empty
   slot → in the function dropdown choose **GameManager → RestartGame ()**.

`RestartGame()` reloads the scene, which resets the score, the obstacles and the
player in one line. Reloading is much less error-prone than manually undoing
everything.

### 8.4 Finish wiring

Select **GameManager** and drag:

* **Game Over Panel** ← `GameOverPanel`
* **Final Score Text** ← `GameOverPanel/FinalScoreText`

Play it: crash on purpose. The panel appears with your score, and **Restart**
starts a fresh run.

---

## Step 9 — Polish: background and difficulty

### 9.1 Scrolling clouds (optional)

`Assets/Scripts/BackgroundScroller.cs`:

```csharp
using UnityEngine;

/// <summary>
/// Optional eye-candy. Slides a background object to the left and wraps it back round,
/// so the world looks like it is moving even though the player stands still.
///
/// Attach to the Background object (or to a cloud). Remove this component
/// (or the whole cloud) if you do not want the effect -- the game works without it.
/// </summary>
public class BackgroundScroller : MonoBehaviour
{
    [Tooltip("How fast this object slides left. Keep it slower than the obstacles.")]
    public float speed = 1f;

    [Tooltip("How far left it may go before it wraps back to where it started.")]
    public float wrapDistance = 30f;

    private Vector3 startPosition;

    private void Start()
    {
        startPosition = transform.position;
    }

    private void Update()
    {
        transform.position += Vector3.left * speed * Time.deltaTime;

        // Wrap around: once it has travelled the whole distance, jump back to the start.
        if (startPosition.x - transform.position.x >= wrapDistance)
        {
            transform.position = new Vector3(transform.position.x + wrapDistance,
                                             transform.position.y,
                                             transform.position.z);
        }
    }
}
```

Add three Sprite objects called **Cloud 1..3** with `Cloud.png`, positions like
`(-6.5, 2.6)`, `(1, 3.6)`, `(7, 2)`, **Order in Layer** `-50`, and attach this
script with **Speed** `0.9`, **Wrap Distance** `22`. They drift slowly and jump
back — cheap parallax.

### 9.2 The sky

An 8 × 256 px vertical gradient, imported at **Pixels Per Unit = 1** (so it is
8 × 256 units) and scaled by `2, 0.046875` gives exactly **16 × 12 units**,
covering the whole camera view. Put it at **Order in Layer** `-100`.

### 9.3 Difficulty curve

Everything lives in `ObstacleSpawner`:

```
speed    : 4.5  + 0.3 * seconds      capped at 15
interval : 1.7  - 0.02 * seconds     floored at 0.85 s
```

After 35 seconds the obstacles are at full speed and arrive every 0.85 s — hard
but fair, since the jump only takes 1.11 s and its peak clears everything.

`Tools/simulate_game.py` replays exactly this maths in Python, so you can check
a change before you try it in the editor:

```
$ python Tools/simulate_game.py
jump apex height     : 3.34 units
tallest obstacle top : 2.60 above the ground
can always clear     : YES
```

---

## Step 10 — Recap

| Requirement | Where it is implemented |
|---|---|
| 2D obstacle-jumping game | `Game.unity` + the six scripts |
| Player that can jump | `PlayerController.cs` (Rigidbody 2D + Physics2D raycast) |
| Obstacles in the path | `Obstacle.prefab` + `ObstacleSpawner.cs` |
| Points for passing obstacles | `ObstacleMover.cs` → `GameManager.AddScore()` |
| Collision ends the game | `PlayerCollision.cs` → `GameManager.GameOver()` |
| Game Over message + final score | `GameOverPanel` (`GameOverTitle`, `FinalScoreText`) |
| Restart | `RestartButton` → `GameManager.RestartGame()` (reloads the scene) |
| Live score on screen | `ScoreText` updated by `GameManager.UpdateScoreText()` |
| Built-in 2D physics | `Rigidbody2D`, `BoxCollider2D`, `Physics2D.Raycast` only |
| Beginner friendly | one responsibility per script, every value visible in the Inspector |

### Common beginner pitfalls (and what this project does about them)

| Pitfall | Fix used here |
|---|---|
| Kinematic player never collides with static obstacles | player is **Dynamic** |
| Player spins after a bump | Rigidbody 2D **Freeze Rotation Z** |
| Ground ray hits the player itself | ray starts *below* the collider bounds |
| Input read in `FixedUpdate` misses clicks | input in `Update`, applied in `FixedUpdate` |
| Obstacle prefab cannot find the manager | static `GameManager.Instance` |
| Restart leaves stale state | restart reloads the scene |
| UI unreadable on other resolutions | Canvas Scaler at `1280 × 720`, aspect 16:9 |
| Game Over fires twice on one crash | `isPlaying` guard in `GameOver()` |

### Where to take it next

* **Real endless runner:** make the player Kinematic-free (`bodyType = Dynamic`),
  give it a constant rightward `velocity.x`, move the camera with a small
  `CameraFollow` script, and recycle the ground and obstacles when they leave
  the view.
* **Coyote time:** allow a jump for ~0.1 s after leaving the ground — remember
  the time of the last `isGrounded == true` and compare with `Time.time`.
* **Variable jump height:** if the player releases the button early, multiply
  `rb.velocity.y` by 0.5 once.
* **Art and audio:** replace the PNGs, add an `AudioSource` to the player and
  call `Play()` from `PlayerController` when jumping.
