import streamlit as st
import time
from pathlib import Path
from src.inference import YOLOInference
from src.utils import save_metadata, load_metadata, get_unique_classes_counts
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
        "search_results":[]
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
                    with st.spinner("Running obj detection"):
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