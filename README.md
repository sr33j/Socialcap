# Socialcap

Socialcap is a Python-based project that analyzes Facebook Messenger data to compute various relationship metrics. It uses a Jupyter notebook to process and visualize the data.

## Getting Started

### Prerequisites

Before you start, ensure you have a Python environment ready. If you don't have Python installed, download it from [Python's official website](https://www.python.org/).

### Installation

Follow these steps to set up Socialcap:

1. **Download Your Facebook Messenger Data**:
   - Navigate to your Facebook settings.
   - Go to "Your Facebook Information".
   - Select "Download Your Information".
   - Choose the "Messages" option and download the data in JSON format.

2. **Environment Setup**:
   - Clone this repository to your local machine.
   - Create a `.env` file in the root directory. Use the `.env.example` as a reference for necessary environment variables.

3. **Install Required Packages**:
   - Open a terminal in the project directory.
   - Run `pip install -r requirements.txt` to install the necessary Python packages.

### Running the Notebook

To analyze your Facebook Messenger data:

1. Place your downloaded Facebook data in the specified directory path.
2. Open the `MessengerWrapped.ipynb` notebook using Jupyter Lab or Jupyter Notebook.
3. Run the cells in the notebook to compute and visualize the relationship metrics.

## Features

- **Data Import**: Load your Facebook Messenger data directly into the notebook.
- **Metric Calculation**: Compute various metrics related to your messaging habits and relationships.
- **Data Visualization**: Graphical representation of insights derived from your data.

## Contributing

Feel free to fork this project and submit pull requests. You can also open an issue for bugs, suggestions, or feature requests.

## License

This project is licensed under the MIT License