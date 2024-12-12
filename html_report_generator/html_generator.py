import os
import base64
import pandas as pd
from pathlib import Path
from collections import defaultdict
import re


def encode_image_to_base64(image_path):
    """Convert an image file to a base64 encoded string."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def detect_and_remove_prefix(name):
    """
    Detect and remove prefix (e.g., '00_') from a filename or folder name.
    
    Parameters:
        name (str): The name of the file or folder.
    
    Returns:
        tuple: (prefix, clean_name)
    """
    match = re.match(r"^(\d+_)?(.+)$", name)
    if match:
        prefix = match.group(1) or ""
        clean_name = match.group(2)
        return prefix, clean_name.strip()
    return "", name.strip()


def sort_files_and_folders(items):
    """
    Sort files or folders by prefix if available.
    
    Parameters:
        items (list of Path): List of Path objects to be sorted.
    
    Returns:
        list of Path: Sorted list of Path objects.
    """
    def extract_key(item):
        prefix, _ = detect_and_remove_prefix(item.name)
        return (int(prefix[:-1]) if prefix else float("inf"), item.name)
    
    return sorted(items, key=extract_key)


def get_html_template():
    """Return the HTML template."""
    return """
    <html>
    <head>
        <title>HTML Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
            .container { max-width: 1000px; margin: auto; background: white; padding: 20px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }
            h1 { text-align: center; color: #333; }
            h2 { border-bottom: 2px solid #4CAF50; color: #4CAF50; padding-bottom: 5px; }
            table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            table, th, td { border: 1px solid #ddd; }
            th, td { padding: 8px; text-align: left; }
            th { background-color: #4CAF50; color: white; }
            .plot { text-align: center; margin: 20px 0; }
            .plot img { max-width: 100%; height: auto; }
            .tabs { display: flex; margin-bottom: 20px; cursor: pointer; justify-content: space-around; }
            .tab { padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px 5px 0 0; flex-grow: 1; text-align: center; margin: 0 5px; }
            .tab.active-tab { background-color: #333; }
            .tab-content { display: none; padding: 20px; border: 1px solid #ddd; border-top: none; background-color: white; }
            .tab-content.active-content { display: block; }
        </style>
    </head>
    <body>
        <div class="container">
    """


def get_html_closing():
    """Return the closing HTML."""
    return """
        </div>
        <script>
            function openTab(evt, tabName) {
                var i, tabcontent, tablinks;
                tabcontent = document.getElementsByClassName("tab-content");
                for (i = 0; i < tabcontent.length; i++) {
                    tabcontent[i].style.display = "none";
                }
                tablinks = document.getElementsByClassName("tab");
                for (i = 0; i < tablinks.length; i++) {
                    tablinks[i].className = tablinks[i].className.replace(" active-tab", "");
                }
                document.getElementById(tabName).style.display = "block";
                evt.currentTarget.className += " active-tab";
            }
            document.addEventListener("DOMContentLoaded", function() {
                document.querySelector(".tab").click();
            });
        </script>
    </body>
    </html>
    """


def generate_html_report(input_path, output_file="report.html"):
    """
    Generate an HTML report from the folder structure.
    
    Parameters:
        input_path (str): Path to the folder containing subfolders with data.
        output_file (str): Path to save the generated HTML file.
    """
    input_path = Path(input_path)
    if not input_path.is_dir():
        raise ValueError(f"{input_path} is not a valid directory.")

    tabs_content = []
    tabs_links = []
    for folder in sort_files_and_folders(input_path.iterdir()):
        if not folder.is_dir():
            continue
        
        _, tab_name = detect_and_remove_prefix(folder.name)
        tab_id = tab_name.replace(" ", "_")
        tabs_links.append(f'<div class="tab" onclick="openTab(event, \'{tab_id}\')">{tab_name}</div>')
        
        tab_content = f'<div id="{tab_id}" class="tab-content">'
        
        # Process CSVs
        for csv_file in sort_files_and_folders(folder.glob("*.csv")):
            _, csv_name = detect_and_remove_prefix(csv_file.stem)
            df = pd.read_csv(csv_file)
            tab_content += f"<h2>{csv_name}</h2>"
            tab_content += df.to_html(index=False, classes="table")
        
        # Process Plots
        for plot_file in sort_files_and_folders(folder.glob("*.png")):
            _, plot_name = detect_and_remove_prefix(plot_file.stem)
            encoded_image = encode_image_to_base64(plot_file)
            tab_content += f"""
            <div class="plot">
                <h3>{plot_name}</h3>
                <img src="data:image/png;base64,{encoded_image}" alt="{plot_name}">
            </div>
            """
        
        tab_content += "</div>"
        tabs_content.append(tab_content)
    
    html_content = get_html_template()
    html_content += f"<h1>HTML Report</h1><div class='tabs'>{''.join(tabs_links)}</div>{''.join(tabs_content)}"
    html_content += get_html_closing()

    with open(output_file, "w") as file:
        file.write(html_content)

    print(f"Report generated at {output_file}")
