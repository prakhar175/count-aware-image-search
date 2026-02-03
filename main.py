import streamlit as st
import json, io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import base64
from src.inference import YOLOInference
from src.utils import save_metadata, load_metadata, get_unique_classes_counts



def img_to_base64(image : Image.Image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

st.markdown(f"""
<style>
.st-emotion-cache-1v0mbdj {{
    width: 100% !important;
    height: 100% !important;
}}

.st-emotion-cache-1wrcr25 {{
    max-width: none !important;
    padding: 0 1rem !important;
}}

.st-emotion-cache-1n76uvr {{
    padding: 0.5rem !important;
}}

.image-card {{
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
    margin-bottom: 20px;
    background: #f8f9fa;
}}

.image-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.15);
}}

.image-container {{
    position: relative;
    width: 100%;
    aspect-ratio: 4/3;
}}

.image-container img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
}}

.meta-overlay {{
    padding: 10px;
    background: rgba(0,0,0,0.85);
    color: white;
    font-size: 13px;
    line-height: 1.4;
}}
</style>
""", unsafe_allow_html=True)

def init_session_state() -> None:
    session_defaults = {
        "metadata": None,
        "unique_class": [],
        "count_options": {},
        "search_params":{
            "search_mode": "Or",
            "selected_classes":[],
            "thresholds":{},
        },
        "search_results":[],
        "show_boxes" : True,
        "grid_cols" : 3,
        "highlight_matches":True
    }
    
    for key,value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key]=value
            
init_session_state()

st.set_page_config(page_title="Smart Image searcher!", page_icon="📄", layout="wide")
st.title("Computer Vision based Image finder", text_alignment="center")

option = st.radio("Choose the option",
                  ( "Process the new images", "Load existing"),
                  horizontal=True)

if option=="Process the new images":
    with st.expander("Process new images", expanded=True):
        col1,col2 = st.columns(2)
        with col1:
            image_dir=st.text_input("Image directory path:", placeholder="path ")
        with col2:
            model_path=st.text_input("Model weight path",placeholder=" eg - yolo11m.pt")
        
    if st.button("Start Inference"):
        if image_dir:
            try :
                with st.spinner("COOKING...."):
                    inference=YOLOInference(model_path)
                    metadata=inference.process_dir(image_dir)
                    metadata_path=save_metadata(metadata,image_dir )
                    
                    st.success(f" Processed {len(metadata)} images !!")
                    st.code(str(metadata_path))
                    st.session_state.metadata = metadata
                    st.session_state.unique_class, st.session_state.count_options = get_unique_classes_counts(metadata)
                    
                    
            except Exception as e:
                st.error("Error :", str(e))
        else:
            st.warning("Enter the path you dumbo")
else:
    with st.expander("Load Exisiting Metadata", expanded=True):
        m_path=st.text_input("Metadata file path:", placeholder="path/to/metadata.json")
        
        if st.button("Load Metadata"):
            if m_path:
                try:
                    with st.spinner("Running obj s"):
                        metadata = load_metadata(m_path)
                        st.success("Successfllu loaaded")                        
                        st.session_state.metadata = metadata
                        st.session_state.unique_class, st.session_state.count_options = get_unique_classes_counts(metadata)
                except Exception as e:
                    st.error("Error", e)
            else:
                st.warning("Path daal be")
                
                
if st.session_state.metadata:
    st.header("Search Engine ")
    
    with st.container():
        st.session_state.search_params['search_mode'] =st.radio("Search mode",
                 ("Or", "And"),
                 horizontal=True)
        
        st.session_state.search_params['selected_classes'] =st.multiselect("Classes to select for :",
                 options=st.session_state.unique_class,
                 )
        if st.session_state.search_params['selected_classes']:
            st.subheader("Count threshold (Optional)")
            cols = st.columns(len(st.session_state.search_params['selected_classes']))
            for i, cls in enumerate(st.session_state.search_params["selected_classes"]):
                with cols[i]:
                    st.session_state.search_params['thresholds']['cls'] = st.selectbox(
                        "Select the Max count", 
                        options=["None"] + st.session_state.count_options[cls])
        
        if st.button("Search Images") and st.session_state.search_params['selected_classes']:
            result = []
            search_params=st.session_state.search_params
            
            for item in st.session_state.metadata:
                matches=False
                class_matches= {}
                
                for cls in search_params["selected_classes"]:
                    class_detections = [d for d in item['detections'] if d['class'] == cls]
                    class_count=len(class_detections)
                    class_matches[cls]=False
                    
                    threshold = search_params['thresholds'].get(cls,"None")
                    if threshold == "None":
                        class_matches[cls] = (class_count>=1)
                    else :
                        class_matches[cls] = (class_count>=1 and class_count<int(threshold))
                        
                if search_params['search_mode'] == 'Or':
                    matches = any(class_matches.values())
                    
                #AND variant
                else:
                    matches = all(class_matches.values())
                    
                if matches:
                    result.append(item)
            st.session_state.search_results = result
            
#Displaying Part

if st.session_state.search_results:
    results = st.session_state.search_results
    search_params = st.session_state.search_params
    
    st.subheader(f"Results: {len(results)} matching images")
    
    with st.expander("Display options:", expanded=True):
        cols = st.columns(3)
        with cols[0]:
            st.session_state.show_boxes = st.checkbox("Show bounding boxes", value=st.session_state.show_boxes)
            
        with cols[1]:
            st.session_state.grid_cols = st.slider("Grid columns",
                      min_value= 2,
                      max_value=5,
                      value=st.session_state.grid_cols)
            
        with cols[2]:
            st.session_state.highlight_matches = st.checkbox("Show Highlights", value=st.session_state.highlight_matches)
        
            
    grid_cols = st.columns(st.session_state.grid_cols)
    col_idx = 0
    
    
    for result in results:
        with grid_cols[col_idx]:
            try:
                img = Image.open(result["img_path"])
                draw = ImageDraw.Draw(img)
                if st.session_state.show_boxes:
                    try:
                        font = ImageFont.truetype("arial.ttf",11)
                    except :
                        font = ImageFont.load_default()
                    for det in result['detections']:
                        cls = det['class']
                        bbox=det['bbox']
                        
                        if cls in search_params["selected_classes"]:
                            color = "#FE564D"
                            thick = 3
                            
                        elif not st.session_state.highlight_matches:
                            color = "#E7DDDD"
                            thick = 1
                        else:
                            continue
                        
                        draw.rectangle(bbox, outline=color, width=thick)

                        if cls in search_params["selected_classes"] or not st.session_state.highlight_matches:
                            label = f"{cls} {det['conf']:.2f}"
                            text_bbox = draw.textbbox((0,0), label, font=font)
                            text_width = text_bbox[2]- text_bbox[0]
                            text_height = text_bbox[3]- text_bbox[1]
                            
                            draw.rectangle([bbox[0], bbox[1],
                                        bbox[0] + text_width + 8,
                                        bbox[1] + text_height + 4],
                                        fill=color)
                            draw.text(
                                (bbox[0] + 4, bbox[1]+2),
                                label, 
                                fill="white",
                                font=font
                            )
                
                meta_item= [f"{k}:{v}" for k , v in result['class_counts'].items() if k in search_params[ "selected_classes"]]
                
                
                st.markdown(f"""
                <div class="image-card">
                    <div class="image-container">
                        <img src="data:image/png;base64,{img_to_base64(img)}">
                    </div>
                    <div class="meta-overlay">
                        <strong>{Path(result['img_path']).name}</strong><br>
                        {", ".join(meta_item) if meta_item else "No matches"}
                    </div>
                </div>
                """, unsafe_allow_html=True)         
                
            except Exception as e:
                st.error(f"Error got: {e}")
                
        col_idx = (col_idx + 1) % st.session_state.grid_cols

    with st.expander("Export Options"):
        st.download_button(
            label="Download Results (JSON)",
            data = json.dumps(results,indent=2),
            file_name="search_results.json",
            mime="application/json"
        )