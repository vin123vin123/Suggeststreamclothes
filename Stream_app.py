import streamlit as st
import requests
import json

# 1. Page Configuration
st.set_page_config(
    page_title="Multi-API Clothing Store",
    page_icon="🛍️",
    layout="wide"
)

# 2. Define Free API Sources & Links
API_SOURCES = {
    "Fake Store API": {
        "url": "https://fakestoreapi.com/products",
        "link": "https://fakestoreapi.com/",
        "description": "A free online REST API for e-commerce testing. We pull curated fashion items from here."
    },
    "Platzi Fake Store API": {
        "url": "https://api.escuelajs.co/api/v1/products",
        "link": "https://platzi.com",
        "description": "Real e-commerce data with high-quality fashion product images and clean JSON outputs."
    }
}

# 3. Main Header & Banner
st.title("👗 Multi-API Digital Clothing Boutique")
st.write("Welcome to the aggregate clothing hub powered concurrently by independent free data platforms.")

# 4. API Directory Layout (Directly on the Home Page)
st.markdown("### 🔗 Direct API Documentation Links")
api_cols = st.columns(2)

for idx, (name, info) in enumerate(API_SOURCES.items()):
    with api_cols[idx]:
        with st.container(border=True):
            st.markdown(f"#### **[{name}]({info['link']})**")
            st.write(info['description'])
            st.caption(f"Endpoint: `{info['url']}`")

st.markdown("---")

# 5. Native Page Filter Selection
st.markdown("### 🗂️ Explore Collections")
app_mode = st.segmented_control(
    "Choose a Store Section:", 
    options=["All Clothing", "Fake Store API Inventory", "Platzi Fashion API Inventory"],
    default="All Clothing"
)

# 6. Safe Data Fetching Functions with Fallbacks
@st.cache_data(ttl=300)
def fetch_fake_store_data():
    try:
        # Fall back to general endpoint if strict category paths go down
        res = requests.get("https://fakestoreapi.com/products", timeout=12)
        if res.status_code == 200:
            all_items = res.json()
            # Filter dynamically on client side safely
            clothing = [
                item for item in all_items 
                if item.get('category', '').lower() in ["men's clothing", "women's clothing", "jewelery"]
            ]
            return clothing if clothing else all_items[:10]
        return []
    except Exception as e:
        st.warning(f"Note: Fake Store API is currently unreachable. Details: {e}")
        return []

@st.cache_data(ttl=300)
def fetch_platzi_data():
    try:
        res = requests.get("https://api.escuelajs.co/api/v1/products", timeout=12)
        if res.status_code == 200:
            return res.json()[:15]
        return []
    except Exception as e:
        st.warning(f"Note: Platzi Fashion API is currently unreachable. Details: {e}")
        return []

# 7. Heavy-Duty URL Cleaning Helper for Platzi API Data
def clean_platzi_image_url(images_field):
    placeholder = "https://placehold.co"
    
    if not images_field:
        return placeholder
        
    # If it is a list, extract the first entry
    raw_url = images_field[0] if isinstance(images_field, list) else str(images_field)
    
    # Repeatedly clean out double-encoded stringified arrays like '["[\"https://...\"]"]'
    for _ in range(3):
        raw_url = raw_url.strip('[]"\' ')
        if raw_url.startswith('["') or raw_url.startswith('['):
            try:
                parsed = json.loads(raw_url)
                raw_url = parsed[0] if isinstance(parsed, list) else str(parsed)
            except:
                pass

    # Filter out known broken mock URLs
    if "placeimg.com" in raw_url or not raw_url.startswith("http"):
        return placeholder
        
    return raw_url

# 8. UI Grid Rendering Helper
def render_product_grid(products, source_type):
    if not products:
        st.info("No items available to display right now from this provider.")
        return

    cols = st.columns(3)
    for i, item in enumerate(products):
        with cols[i % 3]:
            if source_type == "fakestore":
                title = item.get('title', 'Fashion Apparel')
                price = item.get('price', 0.0)
                image_url = item.get('image', "https://placehold.co")
                desc = item.get('description', '')[:100] + "..."
            else: # platzi
                title = item.get('title', 'Platzi Style Clothing')
                price = item.get('price', 0.0)
                image_url = clean_platzi_image_url(item.get('images'))
                desc = item.get('description', '')[:100] + "..."

            with st.container(border=True):
                # Using standard error handling for images
                try:
                    st.image(image_url, use_container_width=True, error_caption="Image unavailable")
                except:
                    st.image("https://placehold.co", use_container_width=True)
                
                st.subheader(f"{title[:35]}")
                st.markdown(f"### **\${price}**")
                st.caption(desc)
                
                if st.button("Add to Cart", key=f"btn_{source_type}_{item.get('id', i)}_{i}"):
                    st.success(f"Added item to cart!")

# 9. Rendering Content Grid
fake_store_products = fetch_fake_store_data()
platzi_products = fetch_platzi_data()

if app_mode == "All Clothing":
    st.markdown("### 🏷️ From: Fake Store API Section")
    render_product_grid(fake_store_products[:6], "fakestore")
    
    st.markdown("---")
    
    st.markdown("### 🏷️ From: Platzi Fashion API Section")
    render_product_grid(platzi_products[:6], "platzi")

elif app_mode == "Fake Store API Inventory":
    st.markdown("## 🛒 Fake Store API Exclusive Feed")
    render_product_grid(fake_store_products, "fakestore")

elif app_mode == "Platzi Fashion API Inventory":
    st.markdown("## 👟 Platzi API Exclusive Feed")
    render_product_grid(platzi_products, "platzi")
