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
