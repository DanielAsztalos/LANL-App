from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from datetime import datetime
from tkinter import messagebox
import os
import shutil
import numpy as np
import sys

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

        for model_name in model_scores.keys():
            train = np.array(model_scores[model_name]["train"])
            model_scores[model_name]["train_avg"] = format(np.mean(train), '.4f')
            test = np.array(model_scores[model_name]["validation"])
            model_scores[model_name]["validation_avg"] = format(np.mean(test), '.4f')

            model_scores[model_name]["train"] = [format(x, '.4f') for x in model_scores[model_name]["train"]]
            model_scores[model_name]["validation"] = [format(x, '.4f') for x in model_scores[model_name]["validation"]]

        template_vars = {
            "title": "Earthquake Prediction Benchmark Report",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model_scores": model_scores,
            "params": params,
            "figures": paths,
            "length": len(model_scores[list(model_scores.keys())[0]]["train"])
        }

        try:
            html_out = self.template.render(template_vars)
            HTML(string=html_out, base_url="./data/report").write_pdf(os.path.join(self.out_path, "report_" + \
                                                                    datetime.now().strftime("%Y%m%d_%H%M%S") + ".pdf"), \
                                                                    stylesheets=self.stylesheets, presentational_hints=True)
        except:
            messagebox.showerror("An error occured in generating the report", sys.exc_info()[0])
            return

        try:
            shutil.rmtree(tmp_folder, ignore_errors=True)
        except:
            pass
        
        messagebox.showinfo("Report saved", "Successfully saved report to the specified location!")

