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
