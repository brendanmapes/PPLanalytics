### This is a copy of the repo originally created within the Public Policy Lab organization by Aman Choudhri. It's been created for sharing access to that repo with Cornell Tech graduate students working with PPL in early 2025. View the original here: https://github.com/Public-Policy-Lab/PPLanalytics.


# ppl-tools

PPL Tools is a desktop application that provides utilities for processing and analyzing interview transcripts and research findings. It currently includes two main features:

1. Airtable Upload: Bulk upload interview transcripts to Airtable.
2. Cluster R3 Findings: Perform natural language processing to cluster similar text entries.

## Getting Started

### For Users

#### Installation

1. Go to the [Releases](https://github.com/yourusername/ppl-tools/releases) page of this repository.
2. Download the latest `.app` file for macOS.
3. Move the `.app` file to your Applications folder.
4. Double-click the app to run it.

#### Usage

Detailed usage instructions for each tool can be found in the application's help menu.

### For Developers

#### Prerequisites

- Python 3.8+
- pip
- Qt 6.7.2+

#### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ppl-tools.git
   cd ppl-tools
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

#### Running the Application

To run the application in development mode:

```
python main.py
```

#### Project Structure

- `main.py`: Entry point of the application
- `ppl_tools/`: Main package
  - `app.py`: Application setup
  - `gui/`: GUI-related modules
    - `airtable_upload/`: Airtable upload feature
    - `clustering/`: Clustering feature
  - `scripts/`: Backend scripts for main functionalities

#### Building the Application

To build the `.app` file using PySide6-Deploy:

1. Ensure you have `pyside6-deploy` installed:
   ```
   pip install pyside6-deploy
   ```

2. Run the deploy command:
   ```
   pyside6-deploy main.py
   ```

3. Follow the prompts to configure your deployment. You may need to specify paths to your project's resources and dependencies.

4. Once the process is complete, the `.app` file will be created in the `dist/` directory.

Note: PySide6-Deploy may require additional configuration depending on your project structure and dependencies. Refer to the [PySide6-Deploy documentation](https://doc.qt.io/qtforpython-6/deployment/index.html) for more detailed instructions and troubleshooting.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- [PySide6](https://wiki.qt.io/Qt_for_Python)
- [Sentence Transformers](https://www.sbert.net/)
- [Plotly](https://plotly.com/python/)
- [scikit-learn](https://scikit-learn.org/)
