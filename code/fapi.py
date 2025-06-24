from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(docs_url=None, redoc_url=None)  # Disable default Swagger UI

# Mount static directories
app.mount("/specs", StaticFiles(directory="api-specs"), name="specs")
app.mount("/swagger-ui", StaticFiles(directory="swagger-ui"), name="swagger-ui")

# Directory for OpenAPI YAML files
SPECS_DIR = "api-specs"

@app.get("/", response_class=HTMLResponse)
async def landing_page():
    # Get list of YAML files in api-specs directory
    spec_files = [
        f for f in os.listdir(SPECS_DIR) if f.endswith((".yaml", ".yml"))
    ]
    # Generate links for each spec
    spec_links = [
        f'<li><a href="/docs/{f.replace(".yaml", "").replace(".yml", "")}">{f.replace(".yaml", "").replace(".yml", "")}</a></li>'
        for f in spec_files
    ]
    links_html = "<ul>" + "".join(spec_links) + "</ul>" if spec_links else "<p>No API specs found.</p>"

    # HTML template for landing page
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Documentation</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1 {{ color: #333; }}
            ul {{ list-style-type: none; padding: 0; }}
            li {{ margin: 10px 0; }}
            a {{ color: #0066cc; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <h1>API Documentation</h1>
        <p>Select an API to view its documentation:</p>
        {links_html}
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/docs/{spec_name}", response_class=HTMLResponse)
async def swagger_ui(spec_name: str):
    # Check if the spec file exists
    spec_file = f"{spec_name}.yaml" if not spec_name.endswith((".yaml", ".yml")) else spec_name
    spec_path = os.path.join(SPECS_DIR, spec_file)
    if not os.path.exists(spec_path):
        raise HTTPException(status_code=404, detail="Spec file not found")

    # HTML template for Swagger UI
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Swagger UI - {spec_name}</title>
        <link rel="stylesheet" href="/swagger-ui/swagger-ui.css" />
        <script src="/swagger-ui/swagger-ui-bundle.js"></script>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script>
            window.onload = () => {{
                SwaggerUIBundle({{
                    url: "/specs/{spec_file}",
                    dom_id: "#swagger-ui",
                    presets: [SwaggerUIBundle.presets.apis],
                }});
            }};
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
