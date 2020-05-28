from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from datetime import datetime
import os
import shutil

class ReportGenerator:
    def __init__(self, env_folder="./data/report", template_file="report-template.html", 
                    out_path="./data/report/", stylesheets=["./data/report/style.css"]):
        self.env_folder = env_folder
        self.template_file = template_file
        self.out_path = out_path
        self.stylesheets = stylesheets

        self.env = Environment(loader=FileSystemLoader(self.env_folder))
        self.template = self.env.get_template(self.template_file)

    def generate_report(self, model_scores, params, figures):
        tmp_folder = "./data/report/tmp"
        os.mkdir(tmp_folder)
        paths = []
        
        for i, fig in enumerate(figures):
            fig.savefig(os.path.join(tmp_folder, "figure_" + str(i) + ".png"), dpi=300, bbox_inches="tight")
            paths.append("tmp/figure_" + str(i) + ".png")

        template_vars = {
            "title": "Earthquake Prediction Benchmark Report",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model_scores": model_scores,
            "params": params,
            "figures": paths
        }

        html_out = self.template.render(template_vars)
        HTML(string=html_out, base_url="./data/report").write_pdf(self.out_path + "report_" + \
                                                                    datetime.now().strftime("%Y%m%d_%H%M%S") + ".pdf", \
                                                                    stylesheets=self.stylesheets, presentational_hints=True)

        # os.rmdir(tmp_folder)
        shutil.rmtree(tmp_folder, ignore_errors=True)



# env = Environment(loader=FileSystemLoader('./data/report'))
# template = env.get_template("report-template.html")

# template_vars = {
#     "title": "Lool",
#     "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#     "model_scores": {"alma": 0, "korte": 1},
#     "params": {"alma": {"param1": 0, "param2": 1}, "korte": {"param0": 12}}
# }

# html_out = template.render(template_vars)

# HTML(string=html_out, base_url="./data/report").write_pdf("./data/report/report1.pdf", stylesheets=["./data/report/style.css"], presentational_hints=True)
