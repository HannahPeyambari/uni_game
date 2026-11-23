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
