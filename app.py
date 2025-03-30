import os

from flask import Flask
from flask_cors import CORS
from static import qdrant_endpoint, askQuestion
from flask import Flask, send_from_directory

app = Flask(__name__)
CORS(app)

app.config['filesToProcess'] = []



app.register_blueprint(qdrant_endpoint.upload_file_bp)
app.register_blueprint(askQuestion.ask_question_bp)

@app.route('/')
def render_index():
    return send_from_directory('templates', 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
