import requests
import streamlit as st
import pandas as pd
import json
from typing import Optional, List, Dict
from io import BytesIO

# API Base URL
API_BASE_URL = "http://localhost:8000/cv"

# Initialize session state
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'experienced_skills' not in st.session_state:
    st.session_state.experienced_skills = pd.DataFrame(columns=['Skill', 'Years of Experience'])

def upload_cv_files():
    """Upload CV files section"""
    st.header("📄 Upload CV Files")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Upload Files")
        uploaded_files = st.file_uploader(
            "Choose CV files", 
            accept_multiple_files=True,
            type=['pdf', 'docx', 'txt']
        )
        
        if st.button("Upload Files", key="upload_files"):
            if uploaded_files:
                files = []
                for file in uploaded_files:
                    files.append(('files', (file.name, file.getvalue(), file.type)))
                
                try:
                    response = requests.post(f"{API_BASE_URL}/upload", files=files)
                    if response.status_code == 200:
                        st.success("Files uploaded successfully!")
                        st.json(response.json())
                    else:
                        st.error(f"Upload failed: {response.status_code}")
                        st.json({"error": response.text})
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.json({"error": str(e)})
            else:
                st.warning("Please select files to upload")
    
    with col2:
        st.subheader("Upload from Google Drive")
        google_drive_url = st.text_input("Google Drive URL")
        
        if st.button("Upload from Google Drive", key="upload_gdrive"):
            if google_drive_url:
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/upload",
                        data={"googleDriveUrl": google_drive_url}
                    )
                    if response.status_code == 200:
                        st.success("Google Drive file uploaded successfully!")
                        st.json(response.json())
                    else:
                        st.error(f"Upload failed: {response.status_code}")
                        st.json({"error": response.text})
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.json({"error": str(e)})
            else:
                st.warning("Please enter Google Drive URL")

def search_cvs():
    """Search CVs section"""
    st.header("🔍 Search CVs")
    
    with st.expander("Basic Search", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
        
        with col2:
            linkedin = st.text_input("LinkedIn")
            git_repo = st.text_input("Git Repository")
            location = st.text_input("Location")
    
    with st.expander("Advanced Search"):
        col1, col2 = st.columns(2)
        
        with col1:
            keywords_input = st.text_input(
                "Keywords (separate by comma)", 
                help="Example: python, machine learning, web development"
            )
            skills_input = st.text_input(
                "Skills (separate by comma)",
                help="Example: Python, React, SQL"
            )
            job_titles_input = st.text_input(
                "Job Titles (separate by comma)",
                help="Example: Software Developer, Data Analyst"
            )
        
        with col2:
            requirement_description = st.text_area(
                "Requirement Description",
                help="Describe the job requirements or candidate profile you're looking for"
            )
    
    with st.expander("Experience Requirements"):
        st.subheader("Skills and Experience Requirements")
        
        # Display current skills table
        if not st.session_state.experienced_skills.empty:
            edited_df = st.data_editor(
                st.session_state.experienced_skills,
                num_rows="dynamic",
                use_container_width=True,
                key="skills_editor"
            )
            st.session_state.experienced_skills = edited_df
        
        # Add new skill form
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            new_skill = st.text_input("Add Skill", key="new_skill_input")
        with col2:
            new_years = st.number_input("Years", min_value=0, max_value=50, value=1, key="new_years_input")
        with col3:
            if st.button("Add Skill", key="add_skill_btn"):
                if new_skill:
                    new_row = pd.DataFrame({
                        'Skill': [new_skill],
                        'Years of Experience': [new_years]
                    })
                    st.session_state.experienced_skills = pd.concat([
                        st.session_state.experienced_skills, new_row
                    ], ignore_index=True)
                    st.rerun()
        
        if st.button("Clear All Skills", key="clear_skills"):
            st.session_state.experienced_skills = pd.DataFrame(columns=['Skill', 'Years of Experience'])
            st.rerun()
    
    # Search button
    if st.button("🔍 Search", key="search_btn", type="primary"):
        # Prepare search query
        search_query = {}
        
        # Basic fields
        if name: search_query["name"] = name
        if email: search_query["email"] = email
        if phone: search_query["phone"] = phone
        if linkedin: search_query["linkedIn"] = linkedin
        if git_repo: search_query["gitRepo"] = git_repo
        if location: search_query["location"] = location
        
        if keywords_input:
            search_query["keywords"] = [k.strip() for k in keywords_input.split(",") if k.strip()]
        if skills_input:
            search_query["skills"] = [s.strip() for s in skills_input.split(",") if s.strip()]
        if job_titles_input:
            search_query["jobTitles"] = [j.strip() for j in job_titles_input.split(",") if j.strip()]
        if requirement_description:
            search_query["requirementDescription"] = requirement_description
        
        if not st.session_state.experienced_skills.empty:
            experienced_skills_dict = {}
            for _, row in st.session_state.experienced_skills.iterrows():
                experienced_skills_dict[row['Skill']] = row['Years of Experience']
            search_query["experiencedSkills"] = experienced_skills_dict
        
        try:
            print(f"Search Query: {json.dumps(search_query, indent=2)}")
            response = requests.post(f"{API_BASE_URL}/search", json=search_query)
            if response.status_code == 200:
                results = response.json()
                st.success(f"Found {len(results)} results")
                st.json(results)
            else:
                st.error(f"Search failed: {response.status_code}")
                st.json({"error": response.text})
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.json({"error": str(e)})

def list_all_cvs():
    """List all CVs with pagination"""
    st.header("📑 All CVs")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        page = st.number_input("Page", min_value=1, value=1)
    with col2:
        page_size = st.selectbox("Page Size", [5, 10, 20, 50], index=1)
    with col3:
        order_by = st.selectbox("Order By", [
            "lastUpdated", "name", "nameDesc", "id"
        ])
    
    if st.button("Load CVs", key="load_cvs"):
        try:
            params = {
                "page": page,
                "size": page_size,
                "orderBy": order_by
            }
            response = requests.get(f"{API_BASE_URL}/", params=params)
            
            if response.status_code == 200:
                data = response.json()
                st.success(f"Loaded page {page}")
                st.json(data)
            else:
                st.error(f"Failed to load CVs: {response.status_code}")
                st.json({"error": response.text})
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.json({"error": str(e)})

def view_cv_details():
    """View detailed CV information"""
    st.header("👁️ View CV Details")
    
    cv_id = st.text_input("Enter CV ID")
    
    if st.button("Get CV Details", key="get_details"):
        if cv_id:
            try:
                response = requests.get(f"{API_BASE_URL}/{cv_id}")
                if response.status_code == 200:
                    cv_data = response.json()
                    st.success("CV details retrieved successfully!")
                    st.json(cv_data)
                else:
                    st.error(f"Failed to get CV details: {response.status_code}")
                    st.json({"error": response.text})
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.json({"error": str(e)})
        else:
            st.warning("Please enter CV ID")

def delete_cv():
    """Delete a CV"""
    st.header("🗑️ Delete CV")
    
    cv_id = st.text_input("Enter CV ID to delete")
    
    if st.button("Delete CV", key="delete_cv", type="secondary"):
        if cv_id:
            try:
                response = requests.delete(f"{API_BASE_URL}/{cv_id}")
                if response.status_code == 200:
                    result = response.json()
                    st.success("CV deleted successfully!")
                    st.json(result)
                else:
                    st.error(f"Failed to delete CV: {response.status_code}")
                    st.json({"error": response.text})
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.json({"error": str(e)})
        else:
            st.warning("Please enter CV ID")

def update_cv():
    """Update CV section"""
    st.header("✏️ Update CV")
    
    cv_id = st.text_input("CV ID to update")
    
    if cv_id:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Upload New File")
            new_file = st.file_uploader("Choose new CV file", type=['pdf', 'docx', 'txt'])
            
            if st.button("Update with File", key="update_file"):
                if new_file:
                    files = [('file', (new_file.name, new_file.getvalue(), new_file.type))]
                    try:
                        response = requests.put(f"{API_BASE_URL}/update/{cv_id}", files=files)
                        if response.status_code == 200:
                            st.success("CV updated successfully!")
                            st.json(response.json())
                        else:
                            st.error(f"Update failed: {response.status_code}")
                            st.json({"error": response.text})
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        st.json({"error": str(e)})
                else:
                    st.warning("Please select a file")
        
        with col2:
            st.subheader("Update with Google Drive")
            new_gdrive_url = st.text_input("New Google Drive URL")
            
            if st.button("Update with Google Drive", key="update_gdrive"):
                if new_gdrive_url:
                    try:
                        response = requests.put(
                            f"{API_BASE_URL}/update/{cv_id}",
                            data={"googleDriveUrl": new_gdrive_url}
                        )
                        if response.status_code == 200:
                            st.success("CV updated successfully!")
                            st.json(response.json())
                        else:
                            st.error(f"Update failed: {response.status_code}")
                            st.json({"error": response.text})
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        st.json({"error": str(e)})
                else:
                    st.warning("Please enter Google Drive URL")

def main():
    """Main application"""
    st.set_page_config(
        page_title="CV Analysis System",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 CV Analysis System")
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    pages = {
        "Upload CVs": upload_cv_files,
        "Search CVs": search_cvs,
        "List All CVs": list_all_cvs,
        "View CV Details": view_cv_details,
        "Update CV": update_cv,
        "Delete CV": delete_cv
    }
    
    selected_page = st.sidebar.selectbox("Choose a page", list(pages.keys()))
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("API Configuration")
    global API_BASE_URL
    api_url = st.sidebar.text_input("API Base URL", value=API_BASE_URL)
    if api_url != API_BASE_URL:
        API_BASE_URL = api_url.rstrip('/') + '/cv'
    
    # Main content
    pages[selected_page]()

if __name__ == "__main__":
    main()