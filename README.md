# GemCinema 📽️ 
Recreate movie scenes with Gemini 3 Pro Image (Nano Banana Pro) and Veo 3.1.

## Run the Web App:

1. Clone the repository on your local machine.
2. Navigate to `cd GemCinema` directory.
3. Run `pip install -r requirements.txt` to install the packages.
4. Open `.env` file and configure your Gemini API key.
5. Run `flask run` to start the server.
6. Open `localhost:5000` on your web browser and enjoy converting your sketches into beautiful paintings.

---

## Architecture

<img src="https://github.com/NSTiwari/GemCinema/blob/main/assets/architecture.jpeg">


---

## Results

### AI-Generated Storyboard (Gemini 3 Pro)
*The images below demonstrate the identity merge where the user's portrait is integrated into original movie frames with matched lighting, grain, and era-specific styling.*

<p align="center">
  <img src="assets/image_0.png" width="48%" />
  <img src="assets/image_1.png" width="48%" />
</p>

### Final Cinematic Premiere (Veo 3.1)
*The final render takes the edited stills as reference images to generate a consistent, high-definition video sequence with natural motion and stable facial identity.*

<img src="https://github.com/NSTiwari/GemCinema/blob/main/assets/video.gif">

<p>
  <a href="https://www.youtube.com/watch?v=U2xOqgkG1RM" style="text-decoration: none; color: inherit;">
    <img src="https://upload.wikimedia.org/wikipedia/commons/0/09/YouTube_full-color_icon_%282017%29.svg" width="20" alt="Watch on YouTube" style="vertical-align: middle;">
    <span style="font-size: 14px; vertical-align: middle; margin-left: 12px;">Watch on YouTube</span>
  </a>
</p>


---

# Acknowledgment:
<img src="https://github.com/NSTiwari/GemCinema/blob/main/assets/dev-logo.png">

This project was developed as part of Google's AI Developer Programs AI Sprint H2 2025. My sincere thanks to the AI Developers Program Team for their generous support in providing GCP credits to help facilitate this project.
