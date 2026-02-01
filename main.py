import streamlit as st
import time
from pathlib import Path
from src.inference import YOLOInference
from src.utils import save_metadata, load_metadata, get_unique_classes_counts
def init_session_state() -> None:
    session_defaults = {
        "metadata": None,
        "unique_class": [],
        "count_options": {}
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
    st.expander("Process new images", expanded=True)
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