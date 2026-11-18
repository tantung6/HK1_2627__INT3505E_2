import os
from flask import Flask, send_file, render_template_string
from blueprints.v1 import bp as v1_bp
from blueprints.v2 import bp as v2_bp

app = Flask(__name__)

# Đăng ký 2 blueprint với url_prefix riêng biệt
app.register_blueprint(v1_bp, url_prefix="/api/v1/users")
app.register_blueprint(v2_bp, url_prefix="/api/v2/users")

# Yêu cầu 2: OpenAPI spec endpoint và Swagger UI trực quan
@app.route("/openapi.yaml")
def openapi_spec():
    yaml_path = os.path.join(os.path.dirname(__file__), "openapi.yaml")
    return send_file(yaml_path, mimetype="text/yaml")

@app.route("/docs")
def swagger_ui():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>User API Documentation (Practice 1)</title>
        <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
        <script>
            SwaggerUIBundle({
                url: '/openapi.yaml',
                dom_id: '#swagger-ui'
            });
        </script>
    </body>
    </html>
    """)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
