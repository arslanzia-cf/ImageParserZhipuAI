import os
import base64
import streamlit as st
from io import BytesIO, StringIO
from PIL import Image
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from zhipuai import ZhipuAI, APIRequestFailedError

zhipuai_api_key = os.getenv('ZHIPUAI_API_KEY', None)

if not zhipuai_api_key:
    st.write(":red[Environment Variable `ZHIPUAI_API_KEY` is not set.]")
    st.stop()

client = ZhipuAI(api_key=zhipuai_api_key)

st.header(":thought_balloon: Smart Resume Parser", anchor=False)
st.subheader(":alien: Powered by Zhipu AI :alien:", anchor=False)
st.divider()

def convert_to_base64(pil_image):
    """
    Convert PIL images to Base64 encoded strings

    :param pil_image: PIL image
    :return: Re-sized Base64 string
    """
    try:
        buffered = BytesIO()
        pil_image.save(buffered, format="JPEG")  # You can change the format if needed
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    except Exception:
        st.write("red[Something went wrong during image processing. Please Try Later.]")
        st.stop()
    return img_str

def convert_pdf_to_txt(file):
    try:
        parse_out = StringIO()
        pdf_resource_manager = PDFResourceManager()
        device = TextConverter(pdf_resource_manager, parse_out, laparams=LAParams())
        interpreter = PDFPageInterpreter(pdf_resource_manager, device)

        for page in PDFPage.get_pages(file, caching=True, check_extractable=True):
            interpreter.process_page(page)
        pdf_text = parse_out.getvalue()

        file.close()
        device.close()
        parse_out.close()
    except Exception:
        st.write("red[Something went wrong during pdf processing. Please Try Later.]")
        st.stop()
    return pdf_text

def parse_image(input_prompt, image_b64):
    try:
        response = client.chat.completions.create(
            model="glm-4v", 
            messages=[{
                "role": "user", 
                "content": [
                        {"type": "text", "text": input_prompt}, 
                        {"type": "image_url", "image_url": {"url": image_b64}}
                            ]
                        }
                    ]
                )
        return response.choices[0].message.content
    except APIRequestFailedError:
        return "Cannot Parse Image Right Now. Please Try Later."

def parse_pdf(input_prompt, pdf_text):
    try:
        response = client.chat.completions.create(
            model="glm-4",
            messages=[
                {"role": "system", "content": f"Answer the question based only on the following resume:\n {pdf_text}"},
                {"role": "user", "content": input_prompt},
                    ],
                )
        return response.choices[0].message.content
    except APIRequestFailedError:
        return "Cannot Parse Image Right Now. Please Try Later."


if __name__ == '__main__':
    input_upload = st.file_uploader("Upload Image/Pdf", type=['pdf', 'jpeg'])

    if input_upload:
        if input_upload.type.split('/')[1] in ('jpg', 'jpeg'):
            pil_image = Image.open(input_upload)
            image_b64 = convert_to_base64(pil_image)

            input_prompt = st.chat_input(placeholder="prompt")

            if input_prompt:
                with st.spinner('Please wait...'):
                    res = parse_image(input_prompt, image_b64)
                    st.write(res)
       
        if input_upload.type.split('/')[1] == 'pdf':
            pdf_text = convert_pdf_to_txt(input_upload)

            input_prompt = st.chat_input(placeholder="prompt")

            if input_prompt:
                with st.spinner('Please wait...'):
                    res = parse_pdf(input_prompt, pdf_text)
                    st.write(res)
