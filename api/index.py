#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Vishwa Gaurav (itsvgin@gmail.com)
Flask API to return random meme images now powered by reddit
"""

import random
import requests
from bs4 import BeautifulSoup
from flask import Flask, send_file, jsonify
from PIL import Image
from io import BytesIO
import logging

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)

def get_new_memes():
    """Scrapes the website and extracts image URLs

    Returns:
        list: List of image URLs
    """
    url = 'https://www.reddit.com/r/ProgrammerHumor/'
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        divs = soup.find_all('div', class_='media-lightbox-img')
        imgs = []
        logging.warning(imgs)
        for div in divs:
            img = div.find('img')['src']
            if img.startswith('https') and img.find('jpeg'):
                imgs.append(img)
        return imgs
    except requests.RequestException as e:
        logging.error(f"Error fetching memes: {e}")
        return []

def serve_pil_image(pil_img):
    """Stores the downloaded image file in-memory
    and sends it as response

    Args:
        pil_img: Pillow Image object

    Returns:
        response: Sends image file as response
    """
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

@app.after_request
def set_response_headers(response):
    """Sets Cache-Control header to no-cache so GitHub
    fetches new image every time
    """
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route("/", methods=['GET'])
def return_meme():
    memes = get_new_memes()
    if not memes:
        return jsonify({"error": "Failed to fetch memes"}), 500
    
    img_url = random.choice(memes)
    try:
        res = requests.get(img_url, stream=True)
        res.raise_for_status()
        res.raw.decode_content = True
        img = Image.open(res.raw)
        return serve_pil_image(img)
    except requests.RequestException as e:
        logging.error(f"Error fetching image: {e}")
        return jsonify({"error": "Failed to fetch image"}), 500
    except IOError as e:
        logging.error(f"Error processing image: {e}")
        return jsonify({"error": "Failed to process image"}), 500

if __name__ == "__main__":
    app.run(debug=True)
