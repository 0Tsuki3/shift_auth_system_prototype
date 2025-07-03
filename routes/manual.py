from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory, session
import os
import shutil
import pandas as pd
from markdown import markdown
from functools import wraps
from flask import safe_join  # 上で import を追加



manual_bp = Blueprint('manual', __name__, url_prefix='/manual')

CATEGORY_FILE = 'data/manuals/categories.csv'
MANUAL_DIR = 'data/manuals'

# ログインチェック
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'account' not in session or session.get('account') != 'admin':
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return wrapper

# ---- カテゴリー管理 ----
def load_categories():
    if not os.path.exists(CATEGORY_FILE):
        return []
    df = pd.read_csv(CATEGORY_FILE)
    return df['category'].tolist()

def save_categories(categories):
    df = pd.DataFrame({'category': categories})
    os.makedirs(os.path.dirname(CATEGORY_FILE), exist_ok=True)
    df.to_csv(CATEGORY_FILE, index=False)

# ---- マニュアル一覧 ----
@manual_bp.route('/view')
def view_manual():
    category = request.args.get('category')
    view_mode = request.args.get('view', 'gallery')
    categories = load_categories()

    files = []
    if category:
        folder = os.path.join(MANUAL_DIR, category)
        if os.path.exists(folder):
            files = [(category, f) for f in os.listdir(folder) if f.endswith('.md')]
    else:
        for c in categories:
            folder = os.path.join(MANUAL_DIR, c)
            if os.path.exists(folder):
                for f in os.listdir(folder):
                    if f.endswith('.md'):
                        files.append((c, f))

    return render_template('manual_view.html',
                           categories=categories,
                           current_category=category,
                           files=files,
                           view_mode=view_mode,
                           account=session.get("account"))

# ---- アップロード ----
@manual_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_manual():
    categories = load_categories()

    if request.method == 'POST':
        category = request.form['category']
        file = request.files['file']
        if category and file:
            folder = os.path.join(MANUAL_DIR, category)
            os.makedirs(folder, exist_ok=True)
            file.save(os.path.join(folder, file.filename))
        return redirect(url_for('manual.view_manual', category=category))

    return render_template('manual_upload.html',
                           categories=categories,
                           account=session.get("account"))

@manual_bp.route('/upload_image', methods=['GET', 'POST'])
@login_required
def upload_manual_image():
    categories = load_categories()

    if request.method == 'POST':
        category = request.form['category']
        image = request.files['image']
        if category and image:
            image_folder = os.path.join(MANUAL_DIR, category, 'images')
            os.makedirs(image_folder, exist_ok=True)
            image.save(os.path.join(image_folder, image.filename))
        return redirect(url_for('manual.view_manual', category=category))

    return render_template('manual_upload_image.html',
                           categories=categories,
                           account=session.get("account"))


# ---- ファイル削除 ----
@manual_bp.route('/delete/<category>/<filename>')
@login_required
def delete_manual(category, filename):
    path = os.path.join(MANUAL_DIR, category, filename)
    if os.path.exists(path):
        os.remove(path)
    return redirect(url_for('manual.view_manual', category=category))

# ---- カテゴリー削除確認 ----
@manual_bp.route('/category/delete_confirm', methods=['POST'])
@login_required
def confirm_delete_category():
    delete_category = request.form.get("delete_category")
    return render_template("manual_category_confirm.html",
                           delete_category=delete_category,
                           account=session.get("account"),
                           role=session.get("role"))

@manual_bp.route('/category/delete', methods=['POST'])
@login_required
def delete_category_final():
    delete_category = request.form.get("delete_category")
    categories = load_categories()
    if delete_category in categories:
        categories.remove(delete_category)
        shutil.rmtree(os.path.join(MANUAL_DIR, delete_category), ignore_errors=True)
        save_categories(categories)
    return redirect(url_for('manual.manage_category'))

@manual_bp.route('/category', methods=['GET', 'POST'])
@login_required
def manage_category():
    categories = load_categories()

    if request.method == 'POST':
        new_category = request.form.get('new_category')
        if new_category and new_category not in categories:
            categories.append(new_category)

            # メインフォルダと images フォルダを両方作成
            category_path = os.path.join(MANUAL_DIR, new_category)
            os.makedirs(category_path, exist_ok=True)

            images_path = os.path.join(category_path, 'images')
            os.makedirs(images_path, exist_ok=True)

            save_categories(categories)

        return redirect(url_for('manual.manage_category'))

    return render_template('manual_category.html',
                           categories=categories,
                           account=session.get("account"),
                           role=session.get("role"))


# ---- Markdownプレビュー ----
@manual_bp.route('/preview/<category>/<path:filename>')
def preview_manual(category, filename):
    path = os.path.join(MANUAL_DIR, category, filename)

    if filename.endswith('.md'):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 画像リンクの変換（altテキスト維持）
        import re
        def replace_img_path(match):
            alt_text = match.group(1)
            img_path = match.group(2)
            return f'![{alt_text}](/manual/preview/{category}/{img_path})'

        content = re.sub(r'!\[(.*?)\]\((images/.*?)\)', replace_img_path, content)

        html = markdown(content, extensions=["extra", "toc", "attr_list"])
        return render_template('manual_preview.html',
                               content=html,
                               category=category,
                               account=session.get("account"))
    else:
        # サブディレクトリ画像もOKに
        return send_from_directory(os.path.join(MANUAL_DIR, category), filename)


