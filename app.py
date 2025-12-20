import os
import time
import io
import cv2
import yt_dlp
import base64
import logging
import traceback
import glob
import shutil
from flask import Flask, render_template, request, jsonify, url_for
from google import genai
from google.genai import types
from PIL import Image
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# =========================================================
# STATIC PROMPTS
# =========================================================

STATIC_INSERT_PROMPT = (
    "Insert the person from the first image into the second image as if they were originally filmed in the scene. "
    "Preserve the person's facial identity exactly. "
    "Match lighting direction, intensity, color temperature, and contrast. "
    "Adjust pose, body alignment, and eye direction to match the scene naturally. "
    "Maintain cinematic realism and consistent color grading."
)

STATIC_REFINE_PROMPT = (
    "Modify the image according to the instructions while preserving the character's facial identity exactly. "
    "Maintain photorealism, correct lighting, and cinematic consistency."
)

STATIC_VIDEO_PROMPT = (
    "Generate cinematic video motion from the reference images. "
    "Maintain exact character identity and facial consistency across all frames. "
    "Use natural camera movement, realistic motion, and stable framing."
)

# --- HELPERS ---

def bytes_to_base64(img_bytes):
    return base64.b64encode(img_bytes).decode('utf-8')

def get_next_scene_index():
    existing_files = glob.glob(os.path.join(UPLOAD_FOLDER, "scene_*.png"))
    if not existing_files: return 0
    indices = []
    for f in existing_files:
        try: indices.append(int(os.path.basename(f).split('_')[1].split('.')[0]))
        except: pass
    return max(indices) + 1 if indices else 0

def get_sorted_files(prefix="scene_"):
    files = glob.glob(os.path.join(UPLOAD_FOLDER, f"{prefix}*.png"))
    files.sort(key=lambda x: int(os.path.basename(x).split('_')[1].split('.')[0]))
    return files

def get_all_scenes_data():
    """Returns dict list: [{'filename': 'scene_0.png', 'data': 'b64...'}, ...]"""
    files = get_sorted_files("scene_")
    results = []
    for path in files:
        with open(path, "rb") as f:
            results.append({
                "filename": os.path.basename(path),
                "data": bytes_to_base64(f.read())
            })
    return results

# --- ROUTES ---

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/reset", methods=["POST"])
def reset():
    try:
        for f in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, f)
            if os.path.isfile(file_path): os.unlink(file_path)
        return jsonify({"status": "cleared"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/extract-yt", methods=["POST"])
def extract_yt():
    data = request.json
    url = data.get("url", "").strip()
    timestamps_str = data.get("timestamps", "10")
    
    if not url:
        current_scenes = get_all_scenes_data()
        if current_scenes: return jsonify({"scenes": current_scenes})
        else: return jsonify({"error": "Please enter a YouTube URL or upload files manually."}), 400

    timestamps = timestamps_str.split(",")
    start_idx = get_next_scene_index()

    ydl_opts = {'format': 'bestvideo', 'quiet': True, 'noplaylist': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            video_url = ydl.extract_info(url, download=False)['url']

        cap = cv2.VideoCapture(video_url)
        for i, ts in enumerate(timestamps):
            try: ts_val = float(ts.strip())
            except ValueError: continue
            cap.set(cv2.CAP_PROP_POS_MSEC, ts_val * 1000)
            success, frame = cap.read()
            if success:
                path = os.path.join(UPLOAD_FOLDER, f"scene_{start_idx + i}.png")
                cv2.imwrite(path, frame)
    except Exception as e:
        logger.error(f"YouTube Extract Error: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify({"scenes": get_all_scenes_data()})

@app.route("/upload-manual", methods=["POST"])
def upload_manual():
    files = request.files.getlist("files")
    start_idx = get_next_scene_index()
    for i, file in enumerate(files):
        if file.filename:
            path = os.path.join(UPLOAD_FOLDER, f"scene_{start_idx + i}.png")
            file.save(path)
    return jsonify({"scenes": get_all_scenes_data()})

@app.route("/reorder-scenes", methods=["POST"])
def reorder_scenes():
    """Renames scene_X.png files based on the list order provided by frontend."""
    try:
        data = request.json
        new_order = data.get("order", []) # ["scene_2.png", "scene_0.png", ...]
        
        # 1. Rename all existing to temp names to avoid collisions
        temp_map = {}
        for fname in new_order:
            src = os.path.join(UPLOAD_FOLDER, fname)
            if os.path.exists(src):
                temp_name = f"temp_{fname}"
                temp_path = os.path.join(UPLOAD_FOLDER, temp_name)
                os.rename(src, temp_path)
                temp_map[fname] = temp_path
        
        # 2. Rename from temp to scene_0, scene_1, etc. based on new order
        for i, original_fname in enumerate(new_order):
            if original_fname in temp_map:
                new_path = os.path.join(UPLOAD_FOLDER, f"scene_{i}.png")
                os.rename(temp_map[original_fname], new_path)
                
        return jsonify({"status": "reordered"})
    except Exception as e:
        logger.error(f"Reorder error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/process-edit", methods=["POST"])
def process_edit():
    try:
        data = request.json
        user_b64 = data.get("user_image").split(",")[-1]
        user_bytes = base64.b64decode(user_b64)
        user_path = os.path.join(UPLOAD_FOLDER, "user_input.png")
        with open(user_path, "wb") as f: f.write(user_bytes)
        
        user_pil = Image.open(user_path)
        prompt = data.get("prompt", "")
        
        # Files are already in correct order (0, 1, 2) thanks to reorder endpoint
        scene_files = get_sorted_files("scene_")
        if not scene_files: return jsonify({"error": "No scenes found"}), 400

        results = []
        for i, path in enumerate(scene_files):
            scene_pil = Image.open(path)
            full_prompt = STATIC_INSERT_PROMPT + " " + prompt
            response = client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=[full_prompt, user_pil, scene_pil],
                config=types.GenerateContentConfig(response_modalities=["IMAGE"])
            )
            for part in response.parts:
                if part.inline_data:
                    img_data = part.inline_data.data
                    with open(os.path.join(UPLOAD_FOLDER, f"edited_{i}.png"), "wb") as f: f.write(img_data)
                    results.append(bytes_to_base64(img_data))
                    break
        return jsonify({"images": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/process-refine", methods=["POST"])
def process_refine():
    try:
        data = request.json
        refine_prompt = data.get("prompt", "")
        edited_files = get_sorted_files("edited_")
        results = []
        for path in edited_files:
            prev_img = Image.open(path)
            full_prompt = STATIC_REFINE_PROMPT + " " + refine_prompt
            response = client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=[full_prompt, prev_img],
                config=types.GenerateContentConfig(response_modalities=["IMAGE"])
            )
            for part in response.parts:
                if part.inline_data:
                    img_data = part.inline_data.data
                    with open(path, "wb") as f: f.write(img_data)
                    results.append(bytes_to_base64(img_data))
                    break
        return jsonify({"images": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/generate-video", methods=["POST"])
def generate_video():
    try:
        data = request.json
        video_prompt = data.get("video_prompt", "")
        edited_files = get_sorted_files("edited_")
        if not edited_files: return jsonify({"error": "No edited images found."}), 400

        refs = []
        for path in edited_files:
            with open(path, "rb") as f: img_bytes = f.read()
            refs.append(types.VideoGenerationReferenceImage(
                image=types.Image(image_bytes=img_bytes, mime_type='image/png'),
                reference_type="asset"
            ))

        full_video_prompt = STATIC_VIDEO_PROMPT + " " + video_prompt
        operation = client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=full_video_prompt,
            config=types.GenerateVideosConfig(reference_images=refs), resolution="1080p"
        )
        while not operation.done:
            time.sleep(5)
            operation = client.operations.get(operation)
            print(operation)

        if not operation.response or not hasattr(operation.response, 'generated_videos') or operation.response.generated_videos is None:
             return jsonify({"error": "Video blocked."}), 500

        video_bytes = client.files.download(file=operation.response.generated_videos[0].video)
        with open(os.path.join(UPLOAD_FOLDER, "final.mp4"), "wb") as f: f.write(video_bytes)
        return jsonify({"video_url": url_for('static', filename='uploads/final.mp4')})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
