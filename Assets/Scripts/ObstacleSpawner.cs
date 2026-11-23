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
