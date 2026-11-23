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
