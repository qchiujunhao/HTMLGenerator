from setuptools import setup, find_packages

setup(
    name="html_report_generator",
    version="0.1",
    description="Generate HTML reports with tabs for CSVs and plots from folder structure.",
    author="Junhao Qiu",
    author_email="",
    packages=find_packages(),
    install_requires=["pandas"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
