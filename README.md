# GemCinema

Place yourself inside any movie scene using Gemini and Veo 3.1. Upload a screenshot or extract frames directly from a YouTube video, upload your photo, and the app composites you into the scene with matched lighting and cinematic styling. The edited frames are then passed to Veo 3.1 to generate a short video of you in the scene.

## How it works

1. **Source frames** - Paste a YouTube URL with timestamps to extract frames at specific moments, or upload screenshots directly. Frames can be drag-and-drop reordered before processing.
2. **Character insert** - Upload your portrait. Gemini edits each frame to place you in the scene, preserving your facial identity while matching the lighting, color grading, and era-specific styling of the original footage.
3. **Refine** - Review the edited frames and send correction instructions if anything looks off. Gemini re-edits in place.
4. **Video generation** - Describe the motion or dialogue. The edited stills are passed as reference images to Veo 3.1, which generates a short cinematic video with natural motion and consistent facial identity across frames.

## Architecture

<img src="https://github.com/NSTiwari/GemCinema/blob/main/assets/architecture.jpeg">

## Results

### AI-Generated Storyboard

*User portrait composited into original movie frames with matched lighting, grain, and era-specific styling.*

<p align="center">
  <img src="assets/image_0.png" width="48%" />
  <img src="assets/image_1.png" width="48%" />
</p>

### Final Cinematic Video

*Edited stills passed as reference images to Veo 3.1 for video generation.*

<img src="https://github.com/NSTiwari/GemCinema/blob/main/assets/video.gif">

<p>
  <a href="https://www.youtube.com/watch?v=U2xOqgkG1RM">
    <img src="https://upload.wikimedia.org/wikipedia/commons/0/09/YouTube_full-color_icon_%282017%29.svg" width="20" alt="Watch on YouTube" style="vertical-align: middle;">
    <span style="font-size: 14px; vertical-align: middle; margin-left: 12px;">Watch on YouTube</span>
  </a>
</p>

## Project structure

```
GemCinema/
├── app.py               # Flask server: frame extraction, Gemini editing, Veo video generation
├── templates/
│   └── index.html       # 5-step carousel UI with drag-and-drop scene reordering
├── static/              # Static assets and uploaded/generated files
├── requirements.txt
└── .env                 # GOOGLE_API_KEY goes here
```

## Steps to run

1. Clone the repository.
2. Navigate to the `GemCinema` directory.
3. Run `pip install -r requirements.txt`.
4. Add your Gemini API key to the `.env` file:
   ```
   GOOGLE_API_KEY=your_key_here
   ```
5. Run `flask run` and open `localhost:5000` in your browser.

## Acknowledgment

<img src="https://github.com/NSTiwari/GemCinema/blob/main/assets/dev-logo.png">

This project was developed as part of Google's AI Developer Programs AI Sprint H2 2025. Thanks to the AI Developer Programs team for providing GCP credits to support this project.
