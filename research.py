import wikipedia
from textwrap import fill
from pathlib import Path

def get_wikipedia_summary(topic, sentences=5):
    """Fetch a summary of the topic from Wikipedia."""
    try:
        summary = wikipedia.summary(topic, sentences=sentences)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Error: The topic '{topic}' is ambiguous. Please be more specific.\nOptions include: {', '.join(e.options[:5])}"
    except wikipedia.exceptions.PageError:
        return f"Error: The topic '{topic}' was not found on Wikipedia."
    except Exception as e:
        return f"Error: An unexpected error occurred: {e}"

def format_research_output(topic, content):
    """Format the research content in a decorative manner."""
    header = f"{'='*40}\nTopic: {topic.title()}\n{'='*40}\n"
    body = fill(content, width=80)
    footer = f"\n{'='*40}\nEnd of Research\n{'='*40}\n"
    return f"{header}\n{body}\n{footer}"

def write_to_file(topic, content, directory='research_outputs'):
    """Write the formatted research content to a text file."""
    Path(directory).mkdir(parents=True, exist_ok=True)
    file_path = Path(directory) / f"{topic.replace(' ', '_')}.txt"
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    return file_path

def research_topic(topic):
    """Main function to perform research and save the output."""
    # Step 1: Get data from Wikipedia
    summary = get_wikipedia_summary(topic)
    
    # Step 2: Format the data
    formatted_content = format_research_output(topic, summary)
    
    # Step 3: Write to a file
    file_path = write_to_file(topic, formatted_content)
    
    return file_path

# Example usage
topic = "Python (programming language)"
research_topic(topic)

