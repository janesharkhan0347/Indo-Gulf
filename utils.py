import os, re, uuid
from werkzeug.utils import secure_filename
from flask import current_app
from PIL import Image


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(file, subfolder='products', max_size=(800, 800)):
    """Save uploaded image securely, resize if needed. Returns filename."""
    if not file or not allowed_file(file.filename):
        return None
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    folder = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    img = Image.open(file)
    img.thumbnail(max_size, Image.LANCZOS)
    img.save(path, optimize=True, quality=85)
    return filename


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text


def make_unique_slug(title, model, existing_id=None):
    from app import db
    base = slugify(title)
    slug = base
    counter = 1
    while True:
        q = model.query.filter_by(slug=slug)
        if existing_id:
            q = q.filter(model.id != existing_id)
        if not q.first():
            break
        slug = f"{base}-{counter}"
        counter += 1
    return slug


GULF_COUNTRIES = ['UAE', 'Saudi Arabia', 'Qatar', 'Oman', 'Kuwait', 'Bahrain']

COUNTRY_FLAGS = {
    'UAE': '🇦🇪',
    'Saudi Arabia': '🇸🇦',
    'Qatar': '🇶🇦',
    'Oman': '🇴🇲',
    'Kuwait': '🇰🇼',
    'Bahrain': '🇧🇭',
    'India': '🇮🇳',
}

DEFAULT_CATEGORIES = [
    {'name': 'Onion',           'slug': 'onion',           'icon': '🧅'},
    {'name': 'Lemon',           'slug': 'lemon',           'icon': '🍋'},
    {'name': 'Chilli',          'slug': 'chilli',          'icon': '🌶️'},
    {'name': 'Coriander',       'slug': 'coriander',       'icon': '🌿'},
    {'name': 'Rice',            'slug': 'rice',            'icon': '🍚'},
    {'name': 'Spices',          'slug': 'spices',          'icon': '🫙'},
    {'name': 'Arabic Perfumes', 'slug': 'arabic-perfumes', 'icon': '🧴'},
    {'name': 'Organic Foods',   'slug': 'organic-foods',   'icon': '🥗'},
    {'name': 'Abaya',           'slug': 'abaya',           'icon': '👘'},
    {'name': 'Modest Fashion',  'slug': 'modest-fashion',  'icon': '👗'},
    {'name': 'Dry Fruits',      'slug': 'dry-fruits',      'icon': '🥜'},
    {'name': 'Tea & Coffee',    'slug': 'tea-coffee',      'icon': '☕'},
]


def seed_categories():
    from models import Category
    from app import db
    for cat in DEFAULT_CATEGORIES:
        if not Category.query.filter_by(slug=cat['slug']).first():
            db.session.add(Category(**cat))
    db.session.commit()