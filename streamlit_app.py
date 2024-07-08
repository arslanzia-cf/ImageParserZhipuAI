import os
import base64
import streamlit as st
from io import BytesIO
from PIL import Image
from zhipuai import ZhipuAI, APIRequestFailedError

zhipuai_api_key = os.getenv('ZHIPUAI_API_KEY', None)

if not zhipuai_api_key:
    st.write(":red[Environment Variable `ZHIPUAI_API_KEY` is not set.]")
    st.stop()

client = ZhipuAI(api_key=zhipuai_api_key)

st.header(":thought_balloon: Smart Image Reader", anchor=False)
st.subheader(":alien: AI-Powered Image Parsing :alien:", anchor=False)
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

def run_api(input_prompt, image_b64):
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


if __name__ == '__main__':
    input_image_upload = st.file_uploader("Upload Image", type='jpeg')
    if input_image_upload:
        pil_image = Image.open(input_image_upload)
        image_b64 = convert_to_base64(pil_image)
        
        input_prompt = st.chat_input(placeholder="prompt")

        if input_prompt:
            with st.spinner('Please wait...'):
                res = run_api(input_prompt, image_b64)
                st.write(res)
