def split_string(input_string):
    max_length = 4096
    if len(input_string) <= max_length:
        return [input_string]

    split_strings = []
    temp_string = ""
    code_block = False
    for line in input_string.split("\n"):
        # Check if line is a code block
        if line.strip().startswith("```"):
            code_block = not code_block

        if len(temp_string + line + "\n") > max_length and not code_block:
            split_strings.append(temp_string)
            temp_string = line + "\n"
        else:
            temp_string += line + "\n"

    if temp_string:
        split_strings.append(temp_string)

    return split_strings


from datetime import datetime


def get_current_day_str():
    return datetime.today().strftime("%Y-%m-%d")


import re


def escape_markdown_v2(text: str):
    # List of special characters that need to be escaped in MarkdownV2
    # Note: This is not a complete list and may need to be updated based on your needs
    special_chars = r"/(_*[\~`>#\+=|\{}.!-])/gi"

    # Use a regex to find special characters that are not part of a MarkdownV2 pattern
    # This is a simplified example and may not cover all cases
    pattern = rf"([{special_chars}])"

    # Add a backslash before each matched special character
    escaped_text = re.sub(pattern, r"\\\1", text)

    return escaped_text


if __name__ == "__main__":
    s = "Certainly! Given your book's goal of teaching developers how to leverage AI as a productivity tool, an effective outline would be structured to progressively build the reader's understanding and skills. Here’s a suggested outline that balances theory, practical application, and showcases real-world examples:\n\n### Introduction\n- **The Evolution of AI in Software Development**: Brief history and current trends.\n- **Why Developers Should Embrace AI**: Benefits of using AI as a productivity tool.\n\n### Part I: Understanding AI in Development\n- **Chapter 1: Basics of AI and Machine Learning**: Definitions, differences, and relevance.\n- **Chapter 2: Overview of AI Technologies Used in Development**: Focus on tools and technologies relevant to developers.\n- **Chapter 3: The Role of AI in Modern Development Processes**: Examples of how AI is transforming development workflows.\n\n### Part II: Setting Up the Environment for AI-Driven Development\n- **Chapter 4: Tools and Platforms**: Comparison of AI tools and platforms most beneficial for developers.\n- **Chapter 5: Integrating AI into Your Development Environment**: Step-by-step guide on setting up and configuring your environment.\n\n### Part III: Practical Applications of AI in Development\n- **Chapter 6: Automating Routine Tasks**: Examples of automation in code generation, testing, and deployment.\n- **Chapter 7: AI for Code Optimization and Analysis**: How AI can help in code review, optimization, and refactoring.\n- **Chapter 8: Leveraging AI for Better Code Security**: Use of AI in identifying vulnerabilities and ensuring code security.\n- **Chapter 9: AI in Debugging and Problem-Solving**: Case studies on how AI can speed up the debugging process.\n\n### Part IV: Advanced Uses of AI in Development\n- **Chapter 10: Machine Learning for Predictive Analysis**: Implementing ML models for project management and predictive maintenance.\n- **Chapter 11: Natural Language Processing (NLP) for Enhanced Coding Efficiency**: Examples of NLP in documentation and code comments.\n- **Chapter 12: Using AI for Custom Tool Development**: Guide to developing your own AI-enhanced tools based on project needs.\n\n### Part V: Building Your AI Skills as a Developer\n- **Chapter 13: Learning Resources and Communities**: Curated list of courses, books, and communities for further learning.\n- **Chapter 14: Best Practices in AI-driven Development**: Dos and Don'ts, ethical considerations, and staying up-to-date with AI advancements.\n- **Chapter 15: The Future of AI in Development**: Insights into emerging trends and how to prepare for them.\n\n### Conclusion\n- **Summarizing the AI Journey for Developers**: Recap of key takeaways.\n- **Next Steps and Action Plan**: Encouraging readers to apply what they have learned.\n\n### Appendices\n- **Glossary of Terms**\n- **List of Tools and Resources**\n- **Frequently Asked Questions (FAQs)**\n\n### Illustrations and Supporting Material\nThroughout the book, include diagrams, flowcharts, and screenshots to illustrate concepts and tools. Code snippets and real-world examples should be used to complement theoretical explanations, making abstract ideas tangible and relatable. Including practical exercises or challenges at the end of each chapter can also encourage active learning and experimentation.\n\nThis outline is structured to first build a solid foundation of understanding about AI in the context of development, followed by practical applications and finally exploring advanced topics and future trends. Tailor the content to your audience's skill level and needs, ensuring it remains accessible, practical, and engaging."
    print(escape_markdown_v2(s))
