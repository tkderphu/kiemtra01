import os
import shutil

src_dir = 'laptop-service'
dst_dir = 'mobile-service'

def replace_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Case-sensitive text replacements
    content = content.replace('laptop_service', 'mobile_service')
    content = content.replace('laptop_db', 'mobile_db')
    content = content.replace('postgres-laptop', 'postgres-mobile')
    content = content.replace('Laptop', 'Mobile')
    content = content.replace('laptop', 'mobile')
    content = content.replace('laptops', 'mobiles')
    content = content.replace('LAPTOP', 'MOBILE')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    if os.path.exists(dst_dir):
        shutil.rmtree(dst_dir)
        
    shutil.copytree(src_dir, dst_dir)
    
    # Rename directories
    old_app_dir = os.path.join(dst_dir, 'laptop_service')
    new_app_dir = os.path.join(dst_dir, 'mobile_service')
    os.rename(old_app_dir, new_app_dir)
    
    # Go through all files and rename/replace text
    for root, dirs, files in os.walk(dst_dir):
        for file in files:
            filepath = os.path.join(root, file)
            # rename files if they contain laptop
            new_file = file.replace('laptop', 'mobile')
            if file != new_file:
                new_filepath = os.path.join(root, new_file)
                os.rename(filepath, new_filepath)
                filepath = new_filepath
                
            if filepath.endswith('.py') or filepath.endswith('.txt') or file == 'Dockerfile':
                replace_in_file(filepath)
                
    print("Mobile service scaffolded successfully!")

if __name__ == '__main__':
    main()
