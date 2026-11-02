"""
Script de evaluare și vizualizare pentru strategia PPO antrenată pe HalfCheetah.
Permite rularea deterministă și înregistrarea unui videoclip al rulării robotului.
"""

import argparse
import gymnasium as gym
import numpy as np
import torch

from model import ActorCritic


def evaluate(checkpoint_path: str, num_episodes: int = 5, record_video: bool = False) -> None:
    """Încarcă un model salvat și evaluează performanța deterministă a strategiei."""
    device = torch.device("cpu")
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)

    obs_dim = checkpoint["obs_dim"]
    act_dim = checkpoint["act_dim"]
    env_id = checkpoint["config"]["env_id"]

    agent = ActorCritic(obs_dim, act_dim)
    agent.load_state_dict(checkpoint["model_state_dict"])
    agent.eval()

    # Aceeași normalizare a observațiilor ca la antrenare, cu statisticile salvate în checkpoint
    obs_mean = checkpoint["obs_mean"]
    obs_std = np.sqrt(checkpoint["obs_var"] + 1e-8)

    # Crearea mediului de evaluare
    render_mode = "rgb_array" if record_video else "human"
    # În videoclip, camera „track” din modelul MuJoCo urmărește robotul, care altfel iese repede din cadru
    camera = {"camera_name": "track"} if record_video else {}
    try:
        env = gym.make(env_id, render_mode=render_mode, **camera)
    except Exception:
        # Dacă mediul grafic nu este disponibil, se continuă fără randare
        render_mode = None
        env = gym.make(env_id)

    if record_video and render_mode == "rgb_array":
        env = gym.wrappers.RecordVideo(
            env,
            video_folder="videoclipuri",
            name_prefix="halfcheetah_ppo",
            episode_trigger=lambda ep: True,
        )

    returns = []
    lengths = []

    print(f"Evaluăm modelul din {checkpoint_path} pe {num_episodes} episoade...")

    for ep in range(1, num_episodes + 1):
        obs, _ = env.reset(seed=100 + ep)
        ep_return = 0.0
        ep_length = 0
        done = False

        while not done:
            with torch.no_grad():
                obs_norm = np.clip((obs - obs_mean) / obs_std, -10.0, 10.0)
                obs_tensor = torch.Tensor(obs_norm).unsqueeze(0)
                action = agent.predict(obs_tensor, deterministic=True)
                action_np = action.squeeze(0).numpy()

            obs, reward, terminated, truncated, _ = env.step(action_np)
            ep_return += reward
            ep_length += 1
            done = terminated or truncated

        returns.append(ep_return)
        lengths.append(ep_length)
        print(f"Episodul {ep}: recompensă = {ep_return:7.1f}, durată = {ep_length} pași")

    env.close()
    print("-" * 50)
    print(f"Recompensă medie: {np.mean(returns):7.1f} ± {np.std(returns):.1f}")
    print(f"Durată medie:     {np.mean(lengths):7.1f} pași")
    if record_video:
        print("Videoclipurile au fost salvate în directorul 'videoclipuri/'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluarea unui model PPO pe HalfCheetah.")
    parser.add_argument(
        "--checkpoint",
        type=str,
        default="checkpoints/ppo_halfcheetah.pt",
        help="Calea către fișierul de model (.pt)",
    )
    parser.add_argument(
        "--episoade",
        type=int,
        default=5,
        help="Numărul de episoade de evaluat",
    )
    parser.add_argument(
        "--video",
        action="store_true",
        help="Activează salvarea videoclipurilor",
    )
    args = parser.parse_args()
    evaluate(args.checkpoint, num_episodes=args.episoade, record_video=args.video)
