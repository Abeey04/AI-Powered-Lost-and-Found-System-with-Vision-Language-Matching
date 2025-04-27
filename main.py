import streamlit as st
import sqlite3
from transformers import BlipProcessor, BlipForConditionalGeneration, BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
from email.mime.text import MIMEText
from PIL import Image
import torch
import os
import shutil
import smtplib

# Initialize the database
def init_db():
    conn = sqlite3.connect('lost_and_found.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS found_items
                 (id INTEGER PRIMARY KEY, caption TEXT, location TEXT, contact TEXT, image_path TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS lost_items
                 (id INTEGER PRIMARY KEY, description TEXT, contact TEXT, email TEXT, status TEXT)''')
    conn.commit()
    conn.close()
 
init_db()

# Load models
@st.cache_resource
def load_models():
    processor = BlipProcessor.from_pretrained(r"C:\Abeey\College\Minor_Proj\MP\Training\5_epoch")
    model = BlipForConditionalGeneration.from_pretrained(r"C:\Abeey\College\Minor_Proj\MP\Training\5_epoch")
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    bert_model = BertModel.from_pretrained('bert-base-uncased')
    return processor, model, tokenizer, bert_model

processor, model, tokenizer, bert_model = load_models()

# Function to generate caption from image
def generate_caption(image):
    inputs = processor(images=image, return_tensors="pt")
    output = model.generate(**inputs)
    caption = processor.decode(output[0], skip_special_tokens=True)
    return caption

# Function to get sentence embedding using BERT
def get_sentence_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = bert_model(**inputs)
    return outputs.last_hidden_state.mean(dim=1)

# Function to compare descriptions and captions
def compare_descriptions(user_description, model_caption):
    user_embedding = get_sentence_embedding(user_description)
    caption_embedding = get_sentence_embedding(model_caption)
    similarity = cosine_similarity(user_embedding.cpu().numpy(), caption_embedding.cpu().numpy())
    return similarity[0][0]

# Function to send email notification
def send_email(to_email, subject, body):
    login = "api"
    password = "52417a86066f4870168fd5e4d24c58c8" 
    sender_email = "hello@demomailtrap.com"
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = to_email

        # Connect to Outlook's SMTP server
        with smtplib.SMTP('live.smtp.mailtrap.io', 587) as server:
            server.starttls()  # Secure the connection
            server.login(login, password)
            server.sendmail(msg['From'], [msg['To']], msg.as_string())

        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

# Function to move found items to the matched folder
def move_to_matched(image_path):
    matched_folder = "matched_found_items/"
    if not os.path.exists(matched_folder):
        os.makedirs(matched_folder)
    new_image_path = shutil.move(image_path, matched_folder)
    return new_image_path

# Database functions
def add_found_item(caption, location, contact, image_path):
    conn = sqlite3.connect('lost_and_found.db')
    c = conn.cursor()
    c.execute("INSERT INTO found_items (caption, location, contact, image_path) VALUES (?, ?, ?, ?)", 
              (caption, location, contact, image_path))
    conn.commit()
    conn.close()

def add_lost_item(description, contact, email, status="lost"):
    conn = sqlite3.connect('lost_and_found.db')
    c = conn.cursor()
    c.execute("INSERT INTO lost_items (description, contact, email, status) VALUES (?, ?, ?, ?)", 
              (description, contact, email, status))
    conn.commit()
    conn.close()

# Retrieve all found items for comparison
def get_all_found_items():
    conn = sqlite3.connect('lost_and_found.db')
    c = conn.cursor()
    c.execute("SELECT * FROM found_items")
    items = c.fetchall()
    conn.close()
    return items

# Retrieve all unmatched lost items
def get_unmatched_lost_items():
    conn = sqlite3.connect('lost_and_found.db')
    c = conn.cursor()
    c.execute("SELECT * FROM lost_items WHERE status='lost'")
    items = c.fetchall()
    conn.close()
    return items

# Match lost items with found items
def match_lost_and_found(lost_description):
    found_items = get_all_found_items()  # Retrieve all found items
    best_match = None
    highest_similarity = 0.0  # Track the highest similarity

    for found_item in found_items:
        found_id, caption, location, contact, image_path = found_item
        similarity_score = compare_descriptions(lost_description, caption)

        if similarity_score > highest_similarity:
            highest_similarity = similarity_score
            best_match = found_item

    if best_match and highest_similarity > 0.6:  # Set threshold at 0.6
        found_id, caption, location, contact, image_path = best_match
        new_image_path = move_to_matched(image_path)

        # Update the found item to matched
        conn = sqlite3.connect('lost_and_found.db')
        c = conn.cursor()
        c.execute("UPDATE found_items SET image_path=? WHERE id=?", (new_image_path, found_id))
        conn.commit()
        conn.close()

        return best_match
    else:
        return None

# Check for matches when a new found item is uploaded
def check_for_lost_matches(new_found_item):
    lost_items = get_unmatched_lost_items()
    conn = sqlite3.connect('lost_and_found.db')
    c = conn.cursor()

    for lost_item in lost_items:
        lost_id, description, contact, email, status = lost_item
        found_id, caption, location, found_contact, image_path = new_found_item
        similarity_score = compare_descriptions(description, caption)

        if similarity_score > 0.6:  # Match found
            # Update lost item to matched
            c.execute("UPDATE lost_items SET status='matched' WHERE id=?", (lost_id,))
            conn.commit()

            # Notify the owner of the lost item
            email_body = (f"We found an item matching your description: {caption}. "
                          f"It was found at {location}. Contact {found_contact} for more details.")
            send_email(email, "Match Found for Your Lost Item!", email_body)

    conn.close()

st.markdown("""
    <style>
    .main-title {
        font-size: 58px; 
        color: #FFFFFF; 
        text-align: center; 
        font-weight: bold;
        margin-bottom: 20px;
    }
    .sub-title {
        font-size: 32px; 
        color: #FFFFFF; 
        text-align: center;
        margin-top: -15px;
        font-weight: lighter;
    }
    .text-body {
        font-size: 18px; 
        text-align: justify; 
        color: #FFFFFF;
        line-height: 1.8;
    }
    .section-title {
        font-size: 26px;
        color: #FFFFFF;
        font-weight: bold;
        margin-top: 30px;
    }
    .cta-button {
        background-color: #e67e22;
        color: white;
        padding: 10px 20px;
        font-size: 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        text-align: center;
    }
    .cta-button:hover {
        background-color: #d35400;
    }
    .feature-icon {
        font-size: 28px; 
        color: #2980b9; 
        margin-right: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Go to", ["Home", "Upload Found Item", "Report Lost Item"])

# Landing Page Content
if page == "Home":
    # Section 1: Introduction
    st.markdown("<h1 class='main-title'>Welcome to Lost & Found Hub</h1>", unsafe_allow_html=True)
    st.markdown("<h2 class='sub-title'>AI-powered Platform for Matching Lost and Found Items</h2>", unsafe_allow_html=True)

    st.markdown("<p class='text-body'>"
                "Lost something precious? Found an item someone might be missing? Look no further! "
                "Our advanced Lost & Found Hub is designed to seamlessly connect lost and found items using "
                "cutting-edge AI. Our platform bridges the gap between people who have found items and those who are desperately searching for them. "
                "By utilizing image recognition and natural language processing, we provide quick, accurate matches to help reunite owners with their lost belongings."
                "</p>", unsafe_allow_html=True)

    # Section 2: Key Features
    st.markdown("<div class='section-title'>Key Features</div>", unsafe_allow_html=True)
    st.markdown("<p class='text-body'>Our platform offers a range of features to ensure the best possible experience for users:</p>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<ul class='text-body'>"
                    "<li><strong><span class='feature-icon'>🖼️</span> AI-powered Image Recognition:</strong> Upload images of found items, and let our AI generate captions for you.</li>"
                    "<li><strong><span class='feature-icon'>📍</span> Location-based Tracking:</strong> Provide the location where the item was found to improve matching accuracy.</li>"
                    "</ul>", unsafe_allow_html=True)
    with col2:
        st.markdown("<ul class='text-body'>"
                    "<li><strong><span class='feature-icon'>🔍</span> Smart Matching:</strong> Use AI-powered descriptions and text matching to find lost items.</li>"
                    "<li><strong><span class='feature-icon'>📧</span> Instant Notifications:</strong> Receive email alerts when a match is found for your lost or found item.</li>"
                    "</ul>", unsafe_allow_html=True)

    # Section 3: How It Works
    st.markdown("<div class='section-title'>How It Works</div>", unsafe_allow_html=True)
    st.markdown("<p class='text-body'>Our platform follows a simple and efficient workflow to ensure that lost items are reunited with their owners as quickly as possible:</p>", unsafe_allow_html=True)
    st.markdown("""
    <ol class='text-body'>
    <li><strong>Found an item?</strong> Upload an image and provide details like location and contact information.</li>
    <li><strong>Lost something?</strong> Submit a detailed report describing your lost item.</li>
    <li>Our AI system continuously scans all uploaded images and descriptions, checking for potential matches.</li>
    <li>If a match is found, both parties are notified via email with instructions on how to proceed.</li>
    </ol>
    """, unsafe_allow_html=True)

    # Section 4: Our Technology Stack
    st.markdown("<div class='section-title'>Our Technology Stack</div>", unsafe_allow_html=True)
    st.markdown("<p class='text-body'>We rely on cutting-edge AI models and tools to power our matching engine:</p>", unsafe_allow_html=True)
    tech_col1, tech_col2 = st.columns(2)
    with tech_col1:
        st.markdown("<p class='text-body'><strong>BLIP (Bootstrapping Language-Image Pre-training):</strong> We use BLIP for image captioning and generating accurate descriptions for found items.</p>", unsafe_allow_html=True)
    with tech_col2:
        st.markdown("<p class='text-body'><strong>BERT (Bidirectional Encoder Representations from Transformers):</strong> BERT allows us to accurately understand user descriptions and compare them to generated captions for matching.</p>", unsafe_allow_html=True)


if page == "Upload Found Item":
    st.markdown("<div class='main-title'>Upload Your Found Item</div>", unsafe_allow_html=True)
    uploaded_image = st.file_uploader("Upload an image of the found item", type=["jpg", "jpeg", "png"])

    if uploaded_image:
        location = st.text_input("Where did you find the item?")
        contact = st.text_input("Enter your contact number", max_chars=10)
        
        # Validate contact number input
        if len(contact) != 10 or not contact.isdigit():
            st.error("Please enter a valid 10-digit contact number.")
        else:
            if location and contact:
                unmatched_folder = "unmatched_found_items/"
                if not os.path.exists(unmatched_folder):
                    os.makedirs(unmatched_folder)

                image = Image.open(uploaded_image).convert("RGB")
                st.image(image, caption="Uploaded Image", use_column_width=True)
                image_path = os.path.join(unmatched_folder, uploaded_image.name)
                image.save(image_path)

                # New caption choice logic
                caption_choice = st.radio("How would you like to generate the caption?", ("Manually Enter", "AI-generated"))
                
                if caption_choice == "Manually Enter":
                    caption = st.text_input("Enter a description of the item")
                elif caption_choice == "AI-generated":
                    caption = generate_caption(image)
                    st.write(f"Generated Caption: **{caption}**")

                # Add a "Proceed" button
                if caption:
                    proceed = st.button("Proceed")
                    
                    if proceed:
                        # Only append to the database when the "Proceed" button is clicked
                        add_found_item(caption, location, contact, image_path)
                        st.success("Found item uploaded successfully!")

                        # Check for matches
                        new_found_item = (None, caption, location, contact, image_path)
                        check_for_lost_matches(new_found_item)
    
    # Explanation and Image Section
    st.markdown("<div class='section-title'>How Our AI Models Help with Matching</div>", unsafe_allow_html=True)
    st.markdown("<p class='text-body'>"
                "Our platform leverages two powerful AI models to help match lost and found items efficiently. Here's how they work:</p>", unsafe_allow_html=True)
    
    # Add Image Explanation
    st.image("mp.png", caption="AI Workflow for Lost & Found Matching", use_column_width=True)  # Make sure to have this image in your directory
    
    # Model Descriptions
    st.markdown("<div class='section-title'>1. BLIP (Bootstrapping Language-Image Pre-training)</div>", unsafe_allow_html=True)
    st.markdown("<p class='text-body'>"
                "BLIP is an advanced AI model that we use to analyze images uploaded by users. When you upload an image of a found item, BLIP generates a natural language description (caption) of the item. "
                "This description includes key details about the object (such as type, color, or any unique features) that will be used to match it with lost items."
                "</p>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>2. BERT (Bidirectional Encoder Representations from Transformers)</div>", unsafe_allow_html=True)
    st.markdown("<p class='text-body'>"
                "BERT is a state-of-the-art natural language processing model that helps us compare the description generated by BLIP with the descriptions of lost items submitted by users. "
                "BERT understands the context and meaning of words, which allows our platform to make intelligent comparisons between descriptions and find matches with high accuracy."
                "</p>", unsafe_allow_html=True)
    
    

    

    # Explanation of the Matching Process
    st.markdown("<div class='section-title'>How Matching Works</div>", unsafe_allow_html=True)
    st.markdown("<p class='text-body'>"
                "After you upload the image and provide the necessary details, our platform will use the generated caption and match it with descriptions of lost items in our database. "
                "If a match is found, you and the item owner will be notified via email, allowing for easy coordination to return the lost item to its rightful owner."
                "</p>", unsafe_allow_html=True)


# Report Lost Item Page
if page == "Report Lost Item":
    st.markdown("<h1 class='main-title'>Report Your Lost Item</h1>", unsafe_allow_html=True)
    # Form Section for Reporting Lost Item
    st.markdown("<div class='section-title'>Describe Your Lost Item</div>", unsafe_allow_html=True)
    
    description = st.text_area("Provide a detailed description of your lost item", placeholder="E.g., Black leather wallet, contains multiple cards, brand logo embossed on the front.")
    
    st.markdown("<div class='section-title'>Your Contact Information</div>", unsafe_allow_html=True)
    st.markdown("""
<style>
input[type='text'], input[type='email'], input[type='password'] {
    -webkit-autofill: off;
    autocomplete: off;
}
</style>
""", unsafe_allow_html=True)
    contact = st.text_input("Enter your contact number", placeholder="E.g., 92345 67890")
    if len(contact) != 10 or not contact.isdigit():
            st.error("Please enter a valid 10-digit contact number.")
    
    email = st.text_input("Enter your email address", placeholder="E.g., example@gmail.com")

    # Submit Button with Success Message
    if description and contact and email:
        if st.button("Submit Report"):
            # Assuming the function `add_lost_item` handles saving the data to the database
            add_lost_item(description, contact, email)
            st.success("Your lost item report has been submitted successfully! We will notify you if a match is found.")

            # AI Matching Process (for explanation, assuming backend implementation)
            st.markdown("<div class='section-title'>Matching in Progress...</div>", unsafe_allow_html=True)
            st.markdown("<p class='text-body'>"
                        "Our system is now scanning the database to find potential matches for your lost item. "
                        "If a match is found, you will receive an email with details about the found item and instructions on how to recover it."
                        "</p>", unsafe_allow_html=True)
            match = match_lost_and_found(description)
            if match:
                found_id, caption, location, found_contact, image_path = match
                st.info(f"Match found! The item was found at {location}. Contact: {found_contact}.")

                # Send email notification for the match
                send_email(email, "Match Found!", f"We found an item matching your description: {caption}. Contact {found_contact}.")
            else:
                st.warning("No match found yet. We'll notify you when a match is available.")

    
    # Explanation Section
    st.markdown("<div class='section-title'>How Reporting Works</div>", unsafe_allow_html=True)
    st.markdown("<p class='text-body'>"
                "If you've lost something valuable, we're here to help! Simply provide a detailed description of the item, along with your contact details. "
                "Our AI system, powered by BERT, will analyze the description and continuously scan through the database of found items. "
                "When a match is found, you'll be notified immediately via email."
                "</p>", unsafe_allow_html=True)

    st.markdown("<p class='text-body'>"
                "To increase the chances of finding your item, please be as specific as possible when describing it. "
                "Mention any distinctive features, colors, brands, or other identifying information. "
                "Our system will compare this information with the captions generated for found items using our BLIP model."
                "</p>", unsafe_allow_html=True)

    # Explanation of Data Collection and AI Matching Process
    st.markdown("<div class='section-title'>How Your Data Is Used</div>", unsafe_allow_html=True)
    st.markdown("<p class='text-body'>"
                "The data you provide is only used to match your lost item with found items. "
                "Once you submit the report, we store it securely in our database and compare it against all available found items. "
                "If a match is found, we'll notify you via the contact information you provided."
                "</p>", unsafe_allow_html=True)
    
    st.markdown("<p class='text-body'>"
                "Our AI models—BERT and BLIP—work in tandem to process and match your report. "
                "BERT analyzes the text description you provide, while BLIP is used to generate captions for any found items uploaded by others. "
                "By using advanced natural language processing and image recognition, we maximize the chances of finding a match."
                "</p>", unsafe_allow_html=True)

    
    # Display Example Image (Optional)
    st.markdown("<div class='section-title'>Example of a Matching Process</div>", unsafe_allow_html=True)
    st.image("Example_captioning.png", caption="Example of a successful match between a lost item and a found item", use_column_width=True)  # Replace with your image file path


