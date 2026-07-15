import os
import re
import yaml

def extract_metadata(content):
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        yaml_text = match.group(1)
        try:
            # استفاده از پارسر استاندارد برای خواندن صحیح لیست‌ها (مثل تگ‌ها)
            return yaml.safe_load(yaml_text) or {}
        except yaml.YAMLError:
            pass
    return {}

def define_env(env):
    @env.macro
    def get_recent_posts(base_folder="posts", limit=6):
        docs_dir = env.conf['docs_dir']
        target_dir = os.path.join(docs_dir, base_folder)
        
        if not os.path.exists(target_dir):
            return f"<p style='color:var(--crimson);'>پوشه {base_folder} یافت نشد.</p>"

        posts = []
        for root, dirs, files in os.walk(target_dir):
            for filename in files:
                if filename.endswith('.md') and filename != 'index.md':
                    filepath = os.path.join(root, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    metadata = extract_metadata(content)
                    
                    if metadata and not metadata.get('draft', False):
                        rel_dir = os.path.relpath(root, docs_dir).replace('\\', '/')
                        url_path = f"{rel_dir}/{filename.replace('.md', '/')}"
                        
                        # در بخش posts.append این کلید را اضافه کنید
                        posts.append({
                            'title': metadata.get('title', 'بدون عنوان'),
                            'category': metadata.get('category', 'عمومی'),
                            'date': metadata.get('date', 'بدون تاریخ'),
                            'excerpt': metadata.get('excerpt', '...'),
                            'image': metadata.get('image', ''), 
                            'tags': metadata.get('tags', []), # این خط اضافه شد
                            'url': url_path
                        })
        
        posts.sort(key=lambda x: x['date'], reverse=True)
        
        html = '<div class="post-grid">\n'
        for post in posts[:limit]:
            img_src = post['image'] if post['image'] else 'assets/images/default-cover.svg'
            # image_html = f'<div class="post-card-image"><img src="{img_src}" alt="{post["title"]}"></div>'
            # image_html = f'<div class="post-card-image"><img src="{img_src}" alt="{post["title"]}" class="no-lightbox"></div>'
            image_html = f'<div class="post-card-image"><img src="{img_src}" alt="{post["title"]}" class="skip-lightbox"></div>'
            # --- بخش جدید: تولید کدهای HTML برای تگ‌ها ---
            tags_html = ''
            if post['tags']:
                tags_html = '<div class="post-card-tags">'
                # برای زیبایی در کارت، نهایتاً ۳ تگ اول را نمایش می‌دهیم
                for tag in post['tags'][:3]: 
                    tags_html += f'<span class="post-card-tag">#{tag}</span>'
                tags_html += '</div>'
            # -----------------------------------------------

            # در این ساختار، کل کارت تبدیل به div شده و لینک‌ها به صورت مجزا به عکس و عنوان داده شده‌اند
            html += f"""
            <div class="post-card">
                <a href="{post['url']}" class="post-card-image">
                    <img src="{img_src}" alt="{post["title"]}">
                </a>
                <div class="post-card-content">
                    <span class="post-category">{post['category']}</span>
                    <h3><a href="{post['url']}" class="card-full-link">{post['title']}</a></h3>
                    <p class="post-excerpt">{post['excerpt']}</p>
                    {tags_html} <!-- تگ‌ها اینجا قرار می‌گیرند -->
                    <div class="post-meta">
                        <span>{post['date']}</span>
                        <span>خواندن</span>
                    </div>
                </div>
            </div>
            """
        html += '</div>\n'
        
        return html