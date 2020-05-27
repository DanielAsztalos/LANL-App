from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from datetime import datetime

env = Environment(loader=FileSystemLoader('./data/report'))
template = env.get_template("report-template.html")

template_vars = {
    "title": "Lool",
    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "model_scores": {"alma": 0, "korte": 1},
    "params": {"alma": {"param1": 0, "param2": 1}, "korte": {"param0": 12}}
}

html_out = template.render(template_vars)

HTML(string=html_out, base_url="./data/report").write_pdf("./data/report/report1.pdf", stylesheets=["./data/report/style.css"], presentational_hints=True)
