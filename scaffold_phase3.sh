#!/bin/bash
ADDONS_DIR="/Users/suraj/Desktop/8848 connect/8848-connect-addons"
MODULES=("8848_franchise" "8848_royalty" "8848_marketing_fee")

for mod in "${MODULES[@]}"; do
    mkdir -p "$ADDONS_DIR/$mod/models"
    mkdir -p "$ADDONS_DIR/$mod/views"
    mkdir -p "$ADDONS_DIR/$mod/security"
    mkdir -p "$ADDONS_DIR/$mod/data"
    
    touch "$ADDONS_DIR/$mod/__init__.py"
    echo "from . import models" > "$ADDONS_DIR/$mod/__init__.py"
    touch "$ADDONS_DIR/$mod/models/__init__.py"
    
    cat << MANIFEST > "$ADDONS_DIR/$mod/__manifest__.py"
{
    'name': '8848 Connect - ${mod}',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Phase 3: ${mod}',
    'author': '8848 Momo House',
    'depends': ['base'],
    'data': [],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
MANIFEST
done

# Set specific dependencies
sed -i '' "s/'depends': \['base'\]/'depends': \['base', 'contacts'\]/" "$ADDONS_DIR/8848_franchise/__manifest__.py"
sed -i '' "s/'depends': \['base'\]/'depends': \['8848_franchise', 'account'\]/" "$ADDONS_DIR/8848_royalty/__manifest__.py"
sed -i '' "s/'depends': \['base'\]/'depends': \['8848_franchise', 'account'\]/" "$ADDONS_DIR/8848_marketing_fee/__manifest__.py"

echo "Scaffold complete"
