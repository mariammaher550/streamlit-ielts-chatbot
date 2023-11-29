import streamlit as st
from openai import OpenAI
import re


# Set your OpenAI API key
# openai.api_key = "YOUR_OPENAI_API_KEY"

# Function to generate an answer using OpenAI API
def generate_answer(task, answer, model_name, openia_api_key):
    prompt = """
you are an IELTS examiner. your task is to evaluate a writing section in an IELTS academic
exam. you have to provide overall band score in <BAND_SCORE> </BAND_SCORE> tags and detailed evaluation in <EVALUATION></EVALUATION> tags . I will provide you the grading
criteria in <CRITERIA> </CRITERIA> tags. The user will send you the task and his answer and you should respond with a feedback on how well does the user follow the grading criteria and his score. Provide his score in this format <Score>Score</Score>.
<CRITERIA>
TASK RESPONSE (TR)
For Task 2 of both AC and GT Writing tests, candidates are required to formulate and
develop a position in relation to a given prompt in the form of a question or
statement, using a minimum of 250 words. Ideas should be supported by evidence,
and examples may be drawn from a candidate’s own experience.
The TR criterion assesses:
▪ how fully the candidate responds to the task.
▪ how adequately the main ideas are extended and supported.
▪ how relevant the candidate’s ideas are to the task.
▪ how clearly the candidate opens the discourse, establishes their position and
formulates conclusions.
▪ how appropriate the format of the response is to the task.
COHERENCE AND COHESION (CC)
This criterion is concerned with the overall organisation and logical development of
the message: how the response organises and links information, ideas and language.
Coherence refers to the linking of ideas through logical sequencing, while cohesion
refers to the varied and appropriate use of cohesive devices (e.g. logical connectors,
conjunctions and pronouns) to assist in making clear the relationships between and
within sentences.
The CC criterion assesses:
▪ the coherence of the response via the logical organisation of information
and/or ideas, or the logical progression of the argument.
▪ the appropriate use of paragraphing for topic organisation and presentation.
▪ the logical sequencing of ideas and/or information within and across
paragraphs.
▪ the flexible use of reference and substitution (e.g. definite articles, pronouns).
▪ the appropriate use of discourse markers to clearly mark the stages in a
response, e.g. [First of all | In conclusion], and to signal the relationship between ideas and/or information, e.g. [as a result | similarly].

LEXICAL RESOURCE (LR)
This criterion refers to the range of vocabulary the candidate has used and the
accuracy and appropriacy of that use in terms of the specific task.
The LR criterion assesses:
▪ the range of general words used (e.g. the use of synonyms to avoid repetition).
▪ the adequacy and appropriacy of the vocabulary (e.g. topic-specific items,
indicators of writer’s attitude).
▪ the precision of word choice and expression.
▪ the control and use of collocations, idiomatic expressions and sophisticated
phrasing.
▪ the density and communicative effect of errors in spelling.
▪ the density and communicative effect of errors in word formation.
GRAMMATICAL RANGE AND ACCURACY (GRA)
This criterion refers to the range and accurate use of the candidate’s grammatical
resource via the candidate’s writing at sentence level.
The GRA criterion assesses:
▪ the range and appropriacy of structures used in a given response (e.g. simple,
compound and complex sentences).
▪ the accuracy of simple, compound and complex sentences.
▪ the density and communicative effect of grammatical errors.
▪ the accurate and appropriate use of punctuation.
</CRITERIA>
"""
    message = [{"role": "system", "content": prompt},
               {"role": "user",
                "content": f"Here is the task:\n <Task>{task}</Task> \n And here is my answer: \n <Answer>{answer}</Answer>"},
               ]
    client = OpenAI(api_key=openia_api_key)

    if "davinci-002" not in model_name:
        response = client.chat.completions.create(
            messages=message,
            model=model_name,
        )
        return response.choices[0].message.content
    else:
        response = client.completions.create(
            model=model_name,
            prompt=prompt,
            max_tokens=1024
        )
        return response.choices[0].text


def extract_score(text):
    """
      Extracting the score from the model's answer
    """
    numbers = re.findall(r'\d+\.\d+|\d+', text.lower())
    return float(numbers[-1]) if numbers and float(numbers[-1]) <= 9 else 6.5


def remove_tags(text):
    cleaned_text = re.sub(r'<[^>]*>', '', text)
    return cleaned_text





# Streamlit app
def main():
    st.title("IELTS Chatbot")
    openai_api_key = st.text_input("Enter your OpenAI API", type="password")
    finetuned_gpt_key = st.text_input("Enter your finetuned GPT API", type="password")
    finetuned_dv02 = st.text_input("Enter your finetuned Dv02 API", type="password")

    # Text input for the task
    task = st.text_area("Enter Your Task:", "")
    answer = st.text_area("Enter your Answer:", "")

    # Dropdown for selecting the model
    model_options = ["gpt-3.5-turbo", "davinci-002", "fine-tuned davinci-002","fine-tuned gpt3.5"]
    selected_model = st.selectbox("Select Model:", model_options)
    if selected_model == "fine-tuned gpt3.5":
        selected_model = finetuned_gpt_key

    if selected_model == "fine-tuned davinci-002":
        selected_model = finetuned_dv02

    # Button to generate the answer
    if st.button("Generate Answer"):
        if task and answer:
            response = generate_answer(task, answer, selected_model, openai_api_key)
            score = extract_score(response)
            cleaned_feedback = remove_tags(response)
            st.text_area("Your overall band score:", score, height=20 * (len(str(score)) // 10 + 1))
            st.text_area("Detailed Feedback:", cleaned_feedback, height=20 * (len(str(cleaned_feedback)) // 10 + 1))
        else:
            st.warning("Please enter a task and an answer before generating a feedback.")


if __name__ == '__main__':
    main()

