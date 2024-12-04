import requests
from bs4 import BeautifulSoup
import math
from transformers import T5Tokenizer, T5ForConditionalGeneration
import re
import concurrent.futures

# Load the HTML file
def get_soup():
    with open("/content/Web_scrapping_project/index.html", "r") as file:
        html_content = file.read()

    # Parse HTML content
    soup = BeautifulSoup(html_content, "html.parser")
    return soup

def calculate_points(generated_output):
    keywords = {
        'name': 2,
        'email': 2,
        'phone number': 1,
        'role': 1,
        'department': 1
    }
    total_points = 0
    for keyword, points in keywords.items():
        if keyword in generated_output.lower():
            total_points += points

    return total_points
def get_dictionary_tag_class():
# List of HTML tags to consider
    soup = get_soup()
    html_tags = ["h1", "h2", "h3", "h4", "h5", "h6", "table", "tr", "th", "td", "a", "ul", "ol", "li", "p", "span", "header",
                "div", "img", "form", "input", "button", "footer", "nav", "section"]

    # Dictionary to store div classes for each tag
    div_classes_dict = {}

    # Extract div classes for each HTML tag
    for tag in html_tags:
        div_classes_list = []
        for element in soup.find_all(tag):
            if element.get("class"):
                div_classes_list.extend(element.get("class"))
        div_classes_list = list(set(div_classes_list))
        div_classes_list = [cls for cls in div_classes_list if cls]
        div_classes_dict[tag] = div_classes_list
    return div_classes_dict


results = {}
def process_div_class(tag, div_class, model, tokenizer):
        result = []
        global results
       
        soup = get_soup()
        elements = soup.find_all(tag, class_=div_class)
        text_content = [element.get_text() for element in elements]
        text_content_str = " ".join(text_content).replace("\n", " ")

        # Split the text content into smaller chunks
        max_tokens = 1000  # Maximum number of tokens per request
        num_chunks = math.ceil(len(text_content_str) / max_tokens)
        chunks = [text_content_str[i * max_tokens: (i + 1) * max_tokens] for i in range(num_chunks)]


        # Make multiple API requests for each chunk
        for chunk in chunks:

            my_text = ""+ chunk + "\nBased on the html content above, \nIs there any person's information?\nOPTIONS\n- Yes \n No"
            input_ids = tokenizer(my_text, return_tensors = "pt").input_ids.to("cuda")
            output1 = model.generate(input_ids, temperature=0.2, top_p = 0.5, top_k = 50)
            output = tokenizer.decode(output1[0], skip_special_tokens= True)

            print("\nOutput: ", text_content_str)
            print("name: ", output)
            print(type(output))

            print()
            
                # if  not output[0]['generated_text'] == "NO": #or output1[0]['generated_text'] == "yes" or output2[0]['generated_text'] == "yes" or output3[0]['generated_text'] == "yes":
            if output == "Yes":
                    
                    result.append([tag, div_class])
                    count = 1
                    if results.get(' '.join(text_content)) is None:
                        results[' '.join(text_content)] = count
                    else:
                        if count > results[' '.join(text_content)]:
                            results[' '.join(text_content)] = count
      



def sort_lines_by_length():
    # Read the content of the input file
    with open("/content/Web_scrapping_project/txt_Files/new_content4.txt", 'r') as file:
        lines = file.readlines()

    # Sort the lines based on their length in descending order (max to min)
    sorted_lines = sorted(lines, key=lambda line: len(line), reverse=True)

    # Write the sorted lines back to the input file
    with open("/content/Web_scrapping_project/txt_Files/new_content5.txt", 'w') as file:
        file.writelines(sorted_lines)


def clean_content(content):
    lines = content.split('\n')
    cleaned_lines = []

    duplicates = set()  # Set to store the duplicate sets of 8 consecutive words

    for line in lines:
        words = line.split()
        for ter in range(len(words), 5, -1):
          for i in range(len(words) - ter):
              word_set = tuple(words[i:i+ter+1])  # Get the set of 8 consecutive words as a tuple
              if word_set in duplicates:
                  # Remove the duplicate set of words
                  words[i:i+5] = [''] * 2
              else:
                  duplicates.add(word_set)

        cleaned_line = ' '.join(words).strip()  # Remove leading and trailing whitespaces
        cleaned_line = re.sub(r'\s+', ' ', cleaned_line)  # Remove unnecessary white spaces
        if cleaned_line:  # Add non-empty lines to the cleaned lines list
            cleaned_lines.append(cleaned_line)

    cleaned_content = '\n'.join(cleaned_lines)
    return cleaned_content

import os
def start_parsing(model, tokenizer):
  

    
    current_directory = os.getcwd()  # Change this to the desired directory path if not in the root directory
    print("Current Directory: ",current_directory)
    # Get the list of files and directories in the current directory
    files_in_directory = os.listdir(current_directory)

    # Print out all the files
    for file in files_in_directory:
        print(file)

    
    div_classes_dict = get_dictionary_tag_class()
    global results
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for tag, div_classes in div_classes_dict.items():
            for div_class in div_classes:
                futures.append(executor.submit(process_div_class, tag, div_class, model, tokenizer))

        # Wait for all the tasks to complete
        concurrent.futures.wait(futures)

    sorted_results = dict(sorted(results.items(), key=lambda x: x[1], reverse=True))

    # Calculate temp_count
    if sorted_results:
        max_count = max(sorted_results.values())
        temp_count = math.ceil(max_count / 2)
    else:
        temp_count = 0

    final_lines = []
    for line, count in sorted_results.items():
        #  if count > temp_count:
                final_lines.append(line)
    final_lines = list(set(final_lines))
    with open("/content/Web_scrapping_project/txt_Files/new_content4.txt", "w") as file:
            for name in list(set([line.lower() for line in final_lines])):
                cleaned_name = ' '.join(name.split())
                print(cleaned_name)
                file.write(cleaned_name + "\n")

    sort_lines_by_length()

    # Read the content from "Version-3/new_content4.txt"
    with open('/content/Web_scrapping_project/txt_Files/new_content5.txt', 'r') as file:
        content = file.read()

    # Clean the content
    cleaned_content = clean_content(content)

    # Remove unnecessary new lines
    cleaned_content = '\n'.join(line for line in cleaned_content.splitlines() if line)

    # Write the cleaned content to "Version-3/cleaned.txt"
    with open('/content/Web_scrapping_project/txt_Files/new_content7.txt', 'w') as file:
        file.write(cleaned_content)
