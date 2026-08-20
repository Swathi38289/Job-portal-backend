"""Run a self-contained demo of the resume screening agent."""

import argparse
import json
import os

import fitz

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jobPortal.settings")

import django

django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient


def build_sample_resume():
    pdf = fitz.open()
    page = pdf.new_page()
    page.insert_text(
        (72, 72),
        "Jane Doe\nPython Django REST API developer\nBuilt backend services and deployed APIs.",
    )
    return SimpleUploadedFile(
        "sample-jane-doe.pdf",
        pdf.tobytes(),
        content_type="application/pdf",
    )


def main():
    parser = argparse.ArgumentParser(description="Run the resume screening demo.")
    parser.add_argument(
        "--semantic",
        action="store_true",
        help="Use sentence-transformer semantic matching.",
    )
    args = parser.parse_args()

    response = APIClient().post(
        "/api/screen/",
        {
            "job_description": "Python Django REST API backend developer",
            "resumes": [build_sample_resume()],
            "use_semantic": str(args.semantic).lower(),
        },
        format="multipart",
    )
    print(f"HTTP {response.status_code}")
    print(json.dumps(response.data, indent=2))


if __name__ == "__main__":
    main()
