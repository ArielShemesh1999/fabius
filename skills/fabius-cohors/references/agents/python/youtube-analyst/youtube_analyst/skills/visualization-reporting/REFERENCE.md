---
name: fabius-cohors-visualization-reporting
description: Turns raw metrics and analysis into visual charts and published shareable HTML reports backed by Google Cloud Storage.
---

### Skill: Visualization & Reporting Workflow

**Objective**: Transform raw data and insights into shareable assets. Know the difference between saving an internal artifact and publishing an external file.

**Execution Steps**:

1. **Confirm Data**: Verify you have the required metrics (e.g., channel engagement rates) or finalized synthesis text.

2. **Visualize**: Delegate to `visualization_agent` with the raw data. It produces a static chart saved as an internal artifact and returns its name.

3. **Retrieve Artifact**: Call `load_artifacts` to load the raw image bytes from session memory.

4. **Publish Image to GCS**: If the HTML report will embed the chart, publish the image first via `publish_file(content, filename, "image/png")`. This returns a public `https://storage.googleapis.com/...` URL.

5. **Construct HTML**: Build a clean HTML string with analysis text. Embed charts using the public GCS URLs (e.g., `<img src="https://storage.../chart.png" />`). Never use local paths.

6. **Final Delivery**:
   - **Internal artifact only**: Call `render_html(html_content, "report.html")` — saves for download later.
   - **Shareable link**: Call `publish_file(html_content, "report.html", "text/html")` — uploads to GCS and returns the public URL.
