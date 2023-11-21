from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader
import openai

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

# Set your OpenAI API key here
openai.api_key = 'your-api-key'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'txt'}

@app.route('/', methods=['POST', 'GET'])
def upload():
    if request.method == 'GET':
        return render_template('index.html')

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        try:
            if file.filename.endswith('.pdf'):
                reader = PdfReader(file)

                if reader.is_encrypted:
                    return jsonify({'error': 'Encrypted PDFs are not supported'}), 400

                text = ''
                for page_num in range(len(reader.pages)):
                    text += reader.pages[page_num].extract_text()

                if not text.strip():
                    return jsonify({'error': 'No text found in the PDF'}), 400

            elif file.filename.endswith('.txt'):
                try:
                    text = file.read().decode('utf-8')
                except UnicodeDecodeError:
                    return jsonify({'error': 'Unable to decode text file. Ensure it is UTF-8 encoded.'}), 400

            else:
                return jsonify({'error': 'Unsupported file type'}), 400

            # Use OpenAI API for document summarization
            summarized_text = summarize_text(text)

            return render_template('result.html', text=summarized_text)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    else:
        return jsonify({'error': 'Invalid file type or size exceeds limit'}), 400

def summarize_text(text):
    # Make a request to OpenAI API for document summarization
    response = openai.Completion.create(
        engine="text-davinci-003",  # Choose the appropriate engine
        prompt=text,
        max_tokens=150,  # Adjust max_tokens as needed
        temperature=0.5  # Adjust temperature as needed
    )

    return response.choices[0].text

if __name__ == '__main__':
    app.run(debug=True)
