# Pezzottaite Phrase

Full-colour Python 3 neon word-catch arcade for [ElbowOS](https://x.com/ElbowOS).

Glyphs fall in six lanes. Steer a raspberry crystal tray and catch the next letter of the phrase. Gold glyphs match. Teal glyphs are decoys. Lock REEL, NEON, ELBOW, PRISM, CHROMA, ARCADE, PULSE, and OS.

Not a ROM, not an emulator, not a clone of the prior hopper / pinball / pipe / breaker packs.

## Play

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 pezzottaite_phrase.py --play
```

A / Left and D / Right move the tray. R restarts.

## Record a 9:16 reel

```bash
python3 pezzottaite_phrase.py --record
```

Headless autoplay writes a 1080x1920, 15s, 30fps H.264 MP4 (`SDL_VIDEODRIVER=dummy`, libx264 yuv420p, CRF 20, +faststart).

- Featured account: https://x.com/ElbowOS
- Drive reel: https://drive.google.com/file/d/1P4d9dqqxeWJJcyg6t9b-bJXe-kNqwDK0/view
