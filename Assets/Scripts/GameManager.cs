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
