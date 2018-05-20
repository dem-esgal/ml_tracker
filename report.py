from os.path import isfile
import logging
import csv

LOGGER = logging.getLogger(__name__)


class Report:
    FIELDNAMES = ["parameters", "metrics", "others", "datasets", "startDTTM", "endDTTM", "attachments", "code",
                  "version"]

    @staticmethod
    def add_report(name, parameters, metrics, others, datasets, start_dttm, end_dttm, attachments, code, version):
        report = dict()
        report["parameters"] = parameters
        report["metrics"] = metrics
        report["others"] = others
        report["datasets"] = datasets
        report["attachments"] = attachments
        report["code"] = code
        report["version"] = version
        report["startDTTM"] = start_dttm.strftime("%Y-%m-%d %H:%M:%S")
        report["endDTTM"] = end_dttm.strftime("%Y-%m-%d %H:%M:%S")

        report_path = "./" + name + ".csv"
        if report_path and isfile(report_path):
            with open(report_path, 'a', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=Report.FIELDNAMES)
                writer.writerow(report)
        else:
            with open(report_path, 'w', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=Report.FIELDNAMES)
                writer.writeheader()
                writer.writerow(report)
