import openai
import openpyxl
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

# Set up your OpenAI API credentials
openai.api_key = 'API'

# Read filtered_information.txt
with open('/content/Web-Scraping-Project/txt_Files/new_content.txt', 'r') as file:
    content = file.read()

# Split the content into chunks
chunk_size = 3500  # Adjust the chunk size as needed
chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]

# Define the prompt template for GPT-3.5 Turbo
prompt_template = """
Input:
{}

Output:
Name:
Role:
Email:
Phone Number:
Department:
"""

# Use GPT-3.5 Turbo to extract information for each chunk
extracted_info = []
for chunk in chunks:
    prompt = prompt_template.format(chunk)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    generated_text = response.choices[0].message.content.strip()
    lines = generated_text.split('\n')
    current_entry = {}
    print(generated_text)

    for line in lines:
        if line.startswith("Name:"):
            if current_entry:
                extracted_info.append(current_entry)
                current_entry = {}
            current_entry["Name"] = line.split("Name:", 1)[1].strip()
        elif line.startswith("Role:"):
            current_entry["Role"] = line.split("Role:", 1)[1].strip()
        elif line.startswith("Email:"):
            current_entry["Email"] = line.split("Email:", 1)[1].strip()
        elif line.startswith("Phone Number:"):
            current_entry["Phone Number"] = line.split("Phone Number:", 1)[1].strip()
        elif line.startswith("Department:"):
            current_entry["Department"] = line.split("Department:", 1)[1].strip()

    # Append the last entry
    if current_entry:
        extracted_info.append(current_entry)

# Authenticate and open the Google Sheet
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("YOUR_SHEET_ACCESS.json", scope)
client = gspread.authorize(credentials)
sheet = client.open("Extracted").sheet1

# Writethe extracted information to the Google Sheet
for entry in extracted_info:
    name = entry.get("Name", "")
    role = entry.get("Role", "")
    email = entry.get("Email", "")
    phone = entry.get("Phone Number", "")
    department = entry.get("Department", "")

    # Create a list of values for the row
    row = [name, role, email, phone, department]

    # Append the row to the sheet
    while True:
        try:
            sheet.append_row(row)
            break  # Break the loop if successful
        except gspread.exceptions.APIError as e:
            if e.response.status_code == 429:
                # Quota exceeded, wait for a minute and retry
                print("Quota exceeded. Waiting for a minute...")
                time.sleep(60)
            else:
                # Handle other API errors
                raise e

print("Data has been written to Google Sheets.")
